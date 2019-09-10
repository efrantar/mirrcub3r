import threading
import time
import ev3

def rot_cmd(ports, deg):
    return b''.join([
        ev3.opOutput_Step_Power,
        ev3.LCX(0),
        ev3.LCX(ports),
        ev3.LCX(100 if deg > 0 else -100),
        ev3.LCX(0),
        ev3.LCX(abs(deg)),
        ev3.LCX(0),
        ev3.LCX(1)
    ])

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

DELAY = {}

DELAY[(False, True, CUT)] = .079
DELAY[(True, False, CUT)] = .057
DELAY[(True, True, CUT)] = .057
DELAY[(False, True, ANTICUT)] = .079 # .0705 # .079
DELAY[(True, False, ANTICUT)] = .057 # .047 # .057
DELAY[(True, True, ANTICUT)] = .0285 # .0445 # .057

DELAY[(False, True, AX_CUT1)] = .079
DELAY[(True, False, AX_CUT1)] = .057
DELAY[(True, True, AX_CUT1)] = .057
DELAY[(False, True, AX_CUT2)] = .086
DELAY[(True, False, AX_CUT2)] = .062
DELAY[(True, True, AX_CUT2)] = .062
DELAY[(False, True, AX_PARTCUT1)] = .079
DELAY[(True, False, AX_PARTCUT1)] = .057
DELAY[(True, True, AX_PARTCUT1)] = .057
DELAY[(False, True, AX_PARTCUT2)] = .086
DELAY[(True, False, AX_PARTCUT2)] = .062
DELAY[(True, True, AX_PARTCUT2)] = .062
DELAY[(False, True, AX_ANTICUT1)] = .079
DELAY[(True, False, AX_ANTICUT1)] = .057
DELAY[(True, True, AX_ANTICUT1)] = .057
DELAY[(False, True, AX_ANTICUT2)] = .086
DELAY[(True, False, AX_ANTICUT2)] = .062
DELAY[(True, True, AX_ANTICUT2)] = .062

DELAY[(False, True, AXAX_CUT)] = 0.086
DELAY[(True, False, AXAX_CUT)] = 0.062
DELAY[(False, True, AXAX_PARTCUT)] = 0.086
DELAY[(True, False, AXAX_PARTCUT)] = 0.062
DELAY[(False, True, AXAX_ANTICUT)] = 0.086
DELAY[(True, False, AXAX_ANTICUT)] = 0.062

HALF_PENALTY1 = .072
HALF_PENALTY2 = .044

AX_DOUBLE_OPT = 0.025
END_DELAY = 0.040 # differentiate between cases to shave off a few extra ms

class Motor:

    SINGLE_DEGS = [0, 90, 180, -180, -90]
    DOUBLE_DEGS = [0, -54, -108, 108, 54]

    def __init__(self, brick, ports, double):
        self.brick = brick
        self.ports = ports
        self.double = double
        self.degs = Motor.DOUBLE_DEGS if double else Motor.SINGLE_DEGS

    def move_cmd(self, count):
        return rot_cmd(self.ports, self.degs[count])

class Robot:

    HOST0 = '00:16:53:40:CE:B6'
    HOST1 = '00:16:53:4A:BA:BA'

    COUNT = [-1, -2, 1]
    FACE_TO_MOTOR = [
        Motor(0, ev3.PORT_A, False),
        Motor(1, ev3.PORT_C + ev3.PORT_D, True),
        Motor(0, ev3.PORT_B + ev3.PORT_C, True),
        Motor(0, ev3.PORT_D, False),
        Motor(1, ev3.PORT_A + ev3.PORT_B, True)
    ] 

    def __init__(self):
        self.bricks = [
            ev3.EV3(protocol='Usb', host=Robot.HOST0), ev3.EV3(protocol='Usb', host=Robot.HOST1)
        ]
    
    def is_double(self, move):
        if is_axial(move):
            move = move[0] # axial moves always have the same gearing
        return Robot.FACE_TO_MOTOR[move // 3].double

    def move(self, m, delay):
        if is_axial(m): # axial move
            m1, m2 = m
            motor1 = Robot.FACE_TO_MOTOR[m1 // 3]
            motor2 = Robot.FACE_TO_MOTOR[m2 // 3]

            # Optimization when exactly one of the two moves is a half-turn; note that this works
            # because faces involved in an axial move always have the same gearing
            if is_half(m1) != is_half(m2):
                print('Test')
                if is_half(m2):
                    m1, m2 = (m2, m1)
                    motor1, motor2 = (motor2, motor1)
                self.bricks[motor1.brick].send_direct_cmd(motor1.move_cmd(Robot.COUNT[m1 % 3]))
                time.sleep(AX_DOUBLE_OPT)
                self.bricks[motor2.brick].send_direct_cmd(motor2.move_cmd(Robot.COUNT[m2 % 3]))
                time.sleep(delay - AX_DOUBLE_OPT - 0.001) # extra transmission delay
                return

            # Axial moves always happen on the same brick
            self.bricks[motor1.brick].send_direct_cmd(
                motor1.move_cmd(Robot.COUNT[m1 % 3]) + motor2.move_cmd(Robot.COUNT[m2 % 3])
            )
            time.sleep(delay)
            return
         
        motor = Robot.FACE_TO_MOTOR[m // 3]
        self.bricks[motor.brick].send_direct_cmd(motor.move_cmd(Robot.COUNT[m % 3])) 
        time.sleep(delay)

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
                delay = DELAY[(
                    self.is_double(sol1[i]), self.is_double(sol1[i + 1]), cut(sol1[i], sol1[i + 1])
                )]
            else:
                delay = END_DELAY
            
            if is_half(sol1[i]):
                delay += HALF_PENALTY2 if self.is_double(sol1[i]) else HALF_PENALTY1
            
            tick = time.time()
            self.move(sol1[i], delay)
            print(time.time() - tick)

