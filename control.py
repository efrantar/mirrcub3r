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

def cut(m1, m2):
    if not is_axial(m1) and is_axial(m2):
        return cut(m2, m1) - 1
    if is_axial(m1) and is_axial(m2):
        return AXAX_CUT + (max(cut(m1, m2[0]), cut(m1, m2[1])) // 2 - 1)

    if not is_axial(m1):
        return CUT if is_clock(m1) != is_clock(m2) else ANTICUT

    m11, m12 = m1
    clock1 = is_clock(m11)
    clock2 = is_clock(m12)

    if is_half(m11):
        if not is_half(m12):
            return CUT if clock1 != is_clock(m2) else ANTICUT
    else:
        if is_half(m12):
            return CUT if clock2 != is_clock(m2) else ANTICUT

    if clock1 == clock2:
        return AX_CUT2 if clock1 != is_clock(m2) else AX_ANTICUT2
    return AX_PARTCUT2

# TODO: tune seriously
CUT_WAITDEG = [
    27, # CUT
    27, # ANTICUT
    27, # AX_CUT1
    27, # AX_CUT2
    27, # AX_PARTCUT1
    27, # AX_PARTCUT2
    27, # AX_ANTICUT1
    27, # AX_ANTICUT2
    27, # AXAX_CUT
    27, # AXAX_PARTCUT
    27  # AXAX_ANTICUT
]
HALF_EXTRA = 41
HOT_CORR = 0 # TODO
SINGLE_ADJ_PRE = 40./24.
SINGLE_ADJ_NXT = 1.

class Motor:

    HOT_TIME = .025 # TODO: tune

    SINGLE_DEGS = [0, 90, 180, -180, -90]
    DOUBLE_DEGS = [0, -54, -108, 108, 54]

    def __init__(self, brick, ports):
        self.brick = brick
        self.ports = ports
        self.double = (ports & (ports - 1)) != 0
        self.degs = Motor.DOUBLE_DEGS if self.double else Motor.SINGLE_DEGS

        self.starttime = 0
        self.turning = 0

    def degrees(self, count):
        deg = self.degs[count] 
        if not self.is_hot():
            self.turning = 0
        deg += self.turning
        self.starttime = time.time()
        self.turning = deg
        return deg

    def is_hot(self):
        return time.time() - self.starttime < Motor.HOT_TIME

# TODO: hot adjustment
# TODO: figure out optimal turning directions for half-turns

def move(motor, count, waitdeg):
    deg = motor.degrees(count)
    rotate(
        motor.brick, motor.ports, deg, waitdeg if waitdeg > 0 else abs(deg) - 5
    )

# TODO: move with worse corner cutting should be the one we wait for
def move1(motor1, motor2, count1, count2, waitdeg):
    deg1 = motor1.degrees(count1)
    deg2 = motor2.degrees(count2)
    if waitdeg <= 0:
        waitdeg = max(deg1, deg2) - 5
    if (abs(count1) == 2) != (abs(count2) == 2):
        if abs(count2) == 2:
            motor1, motor2 = motor2, motor1
            deg1, deg2 = deg2, deg1
        rotate2(
            motor1.brick, motor1.ports, motor2.ports, deg1, deg2,
            15 if motor1.double else 25, waitdeg # at this point any corner-cutting should be over
        )
    else:
        rotate1(motor1.brick, motor1.ports, motor2.ports, deg1, deg2, waitdeg)

class Robot:

    HOST0 = '00:16:53:40:CE:B6'
    HOST1 = '00:16:53:4A:BA:BA'

    COUNT = [-1, -2, 1]
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
                waitdeg = CUT_WAITDEG[cut(sol1[i], sol1[i + 1])]
                if is_half(sol1[i]):
                    waitdeg += HALF_EXTRA
                if not self.is_double(sol1[i]) and self.is_double(sol1[i + 1]):
                    waitdeg *= SINGLE_ADJ_PRE
                if self.is_double(sol1[i]) and not self.is_double(sol1[i + 1]):
                    waitdeg *= SINGLE_ADJ_NXT
            else:
                waitdeg = -1            
            waitdeg = int(waitdeg)

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
        return is_pressed(self.bricks[1], 3) # Tight button

    def scramble_pressed(self):
        return is_pressed(self.bricks[0], 0) # Left button

