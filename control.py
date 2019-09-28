# Robot control.

from cmd import *
import time
import ev3

def are_parallel(m1, m2):
    return abs(m1 // 3 - m2 // 3) == 3

def is_axial(move):
    return isinstance(move, tuple)

def is_half(move):
    if is_axial(move):
        return is_half(move[0]) or is_half(move[1])
    return move % 3 == 1

def is_clock(move):
    return move % 3 <= 1 # TODO: for now all half-turns are considered to be clockwise

# All possible corner cutting situations
CUT = 0
ANTICUT = 1
AX_CUT1 = 2 # simple -> axial
AX_CUT2 = 3 # axial -> simple
AX_PARTCUT1 = 4
AX_PARTCUT2 = 5
AX_ANTICUT1 = 6
AX_ANTICUT2 = 7
AXAX_CUT = 8
AXAX_PARTCUT = 9
AXAX_ANTICUT = 10

def cut(m1, m2, inverted=False):
    if is_axial(m1) and not is_axial(m2):
        return cut(m2, m1, inverted=True) + 1
    if is_axial(m1) and is_axial(m2):
        return AXAX_CUT + (max(cut(m1, m2[0]), cut(m1, m2[1])) // 2 - 1)
    
    if not is_axial(m2):
        return CUT if is_clock(m1) != is_clock(m2) else ANTICUT
    
    m21, m22 = m2
    clock1 = is_clock(m21)
    clock2 = is_clock(m22)

    # Note that a special axial move only yields a simple incoming cut but not
    # an outcoming one
    if not inverted:
        if is_half(m21):
            if not is_half(m22):
                return CUT if clock1 != is_clock(m1) else ANTICUT
        else:
            if is_half(m22):
                return CUT if clock2 != is_clock(m1) else ANTICUT

    if clock1 == clock2:
        return AX_CUT1 if clock1 != is_clock(m1) else AX_ANTICUT1
    return AX_PARTCUT1

# Actually the solver supports different tuning values for all corner cutting situtations
# including the involved motor types (single or double). However, for now this is mostly
# disabled (i.e. the same values everywhere) since the whole process is very tedious,
# in particular due to the fact that values for double motors cannot easily be converted
# into ones for single motors and vice-versa. This yields a huge amount of cases to consider
# that furthermore cannot easily be tweaked in isolation. Theoretically we can probably
# squeeze out 100-200ms in exchange for a bit of consistency with this, however we will
# for now defer this feature to a future iteration of the robot with unfiorm motors.

WAITDEG = {}

WAITDEG[(False, True, CUT)] = 45 # 45
WAITDEG[(True, False, CUT)] = 27 # 20
WAITDEG[(True, True, CUT)] = 27 # 18
WAITDEG[(False, True, ANTICUT)] = 45 # 40
WAITDEG[(True, False, ANTICUT)] = 27 # 18
WAITDEG[(True, True, ANTICUT)] = 27 # 16

WAITDEG[(False, True, AX_CUT1)] = 45 # 45
WAITDEG[(True, False, AX_CUT1)] = 27 # 22
WAITDEG[(True, True, AX_CUT1)] = 27 # 24
WAITDEG[(False, True, AX_CUT2)] = 45 # 45
WAITDEG[(True, False, AX_CUT2)] = 27 # 24
WAITDEG[(True, True, AX_CUT2)] = 27 # 24
WAITDEG[(False, True, AX_PARTCUT1)] = 45 # 45
WAITDEG[(True, False, AX_PARTCUT1)] = 27 # 20
WAITDEG[(True, True, AX_PARTCUT1)] = 27 # 22
WAITDEG[(False, True, AX_PARTCUT2)] = 45 # 45
WAITDEG[(True, False, AX_PARTCUT2)] = 27 # 24
WAITDEG[(True, True, AX_PARTCUT2)] = 27 # 24
WAITDEG[(False, True, AX_ANTICUT1)] = 45 # 40
WAITDEG[(True, False, AX_ANTICUT1)] = 27 # 18
WAITDEG[(True, True, AX_ANTICUT1)] = 27 # 22
WAITDEG[(False, True, AX_ANTICUT2)] = 45 # 50 # we get annoying hotness problems with lower values here
WAITDEG[(True, False, AX_ANTICUT2)] = 27 # 24
WAITDEG[(True, True, AX_ANTICUT2)] = 27 # 24

WAITDEG[(False, True, AXAX_CUT)] = 45 # 45
WAITDEG[(True, False, AXAX_CUT)] = 27 # 27
WAITDEG[(False, True, AXAX_PARTCUT)] = 45 # 45
WAITDEG[(True, False, AXAX_PARTCUT)] = 27 # 27
WAITDEG[(False, True, AXAX_ANTICUT)] = 45 # 35
WAITDEG[(True, False, AXAX_ANTICUT)] = 27 # 27 # hotness again ...

WAITDEG_HALF1 = 70
WAITDEG_HALF2 = 41 
NOT_EARLY = 15 # to make sure we never deadlock with the final move
SPECIAL_AX_WAITDEG1 = 10
SPECIAL_AX_WAITDEG2 = 5

# One very annoying problem with the robot moveset is that when the same motor
# is rotated again before its previous move is entirely complete, then the second
# command simply completes the inital movement rather than performing another move.
# This may happen for instance in a U R U maneuver if R returns before the U-motor
# is fully stopped. In such a situation we actually have to perform U2 to get the
# desired U move. The main purpose of this class is to handle this "hotness".
# Fortunately, with the current tuning values this will bascially never happen.
# However, this will certainly become relevant again in a future iteration of the 
# robot and hence we leave it in.
class Motor:

    # TODO: this should be sufficient for now
    HOT_TIMES = [.000, .025, .045]
    
    SINGLE_DEGS = [0, 90, 180, -180, -90]
    DOUBLE_DEGS = [0, -54, -108, 108, 54]

    def __init__(self, brick, ports):
        self.brick = brick
        self.ports = ports
        self.double = (ports & (ports - 1)) != 0
        self.degs = Motor.DOUBLE_DEGS if self.double else Motor.SINGLE_DEGS

        self.endtime = 0
        self.turning = 0
        self.prev_count = 0

    def degrees(self, count):
        return self.degs[count]

    def is_hot(self):
        return time.time() - self.endtime < Motor.HOT_TIMES[self.prev_count]     

    def begin(self, count):
        deg = self.degrees(count)
        if not self.is_hot():
            self.turning = 0
        else:
            print('Hot') # for debugging purposes
        deg += self.turning
        self.turning = deg
        self.prev_count = abs(count)
        return deg

    def end(self):
        self.endtime = time.time()

def move(motor, count, waitdeg):
    deg = motor.begin(count)
    rotate(
        motor.brick, motor.ports, deg,
        waitdeg if waitdeg > 0 else abs(motor.degrees(count)) - NOT_EARLY
    )
    motor.end()

# TODO: I guess it would be ideal to wait for the move with worse corner cutting?
def move1(motor1, motor2, count1, count2, waitdeg):
    deg1 = motor1.begin(count1)
    deg2 = motor2.begin(count2)
    if waitdeg <= 0:
        waitdeg = max(abs(motor1.degrees(count1)), abs(motor2.degrees(count2))) - NOT_EARLY
    if (abs(count1) == 2) != (abs(count2) == 2):
        print('2')
        if abs(count2) == 2:
            motor1, motor2 = motor2, motor1
            deg1, deg2 = deg2, deg1
        rotate2(
            motor1.brick, motor1.ports, motor2.ports, deg1, deg2,
            SPECIAL_AX_WAITDEG2 if motor1.double else SPECIAL_AX_WAITDEG1, waitdeg
        )
    else:
        rotate1(motor1.brick, motor1.ports, motor2.ports, deg1, deg2, waitdeg)
    motor1.end()
    motor2.end()

class Robot:

    HOST0 = '00:16:53:40:CE:B6'
    HOST1 = '00:16:53:4A:BA:BA'

    COUNT = [-1, -2, 1] # we have to invert directions from the perspective of the motors
    FACE_TO_MOTOR = [
        Motor(0, ev3.PORT_A),
        Motor(1, ev3.PORT_C + ev3.PORT_D),
        Motor(0, ev3.PORT_B + ev3.PORT_C),
        Motor(0, ev3.PORT_D),
        Motor(1, ev3.PORT_A + ev3.PORT_B)
    ]

    def __init__(self):
        self.bricks = [
            ev3.EV3(protocol='Usb', host=Robot.HOST0), ev3.EV3(protocol='Usb', host=Robot.HOST1)
        ]
        for m in Robot.FACE_TO_MOTOR:
            m.brick = self.bricks[m.brick]

    def is_double(self, move):
        if is_axial(move):
            move = move[0] # axial moves always have the same gearing
        return Robot.FACE_TO_MOTOR[move // 3].double

    def execute(self, sol):
        if len(sol) == 0:
            return

        sol1 = []
        i = 0
        while i < len(sol):
            if i < len(sol) - 1 and are_parallel(sol[i], sol[i + 1]):
                sol1.append((sol[i], sol[i + 1]))
                i += 2
            else:
                sol1.append(sol[i])
                i += 1
        print(len(sol1), sol1)

        for i in range(len(sol1)):
            if i < len(sol1) - 1:
                print(sol1[i], cut(sol1[i], sol1[i + 1]))
                waitdeg = WAITDEG[self.is_double(sol1[i]), self.is_double(sol1[i + 1]), cut(sol1[i], sol1[i + 1])]
                if is_half(sol1[i]):
                    waitdeg += WAITDEG_HALF2 if self.is_double(sol1[i]) else WAITDEG_HALF1
            else:
                waitdeg = -1

            tick = time.time()
            if is_axial(sol1[i]):
                m1, m2 = sol1[i]
                move1(
                    Robot.FACE_TO_MOTOR[m1 // 3], Robot.FACE_TO_MOTOR[m2 // 3], 
                    Robot.COUNT[m1 % 3], Robot.COUNT[m2 % 3], 
                    waitdeg
                )
            else:
                move(Robot.FACE_TO_MOTOR[sol1[i] // 3], Robot.COUNT[sol1[i] % 3], waitdeg)
            print(waitdeg, time.time() - tick)

    def solve_pressed(self):
        return is_pressed(self.bricks[1], 3) # Right button

    def scramble_pressed(self):
        return is_pressed(self.bricks[0], 0) # Left button

