import threading
import time
import ev3

def command(ports, deg):
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

def rotate1(brick, ports, deg):
    brick.send_direct_cmd(command(ports, deg))

def rotate2(brick, ports1, deg1, ports2, deg2):
    brick.send_direct_cmd(
        command(ports1, deg1) + command(ports2, deg2)
    )

class MotorType:

    def __init__(self, degs, waits, penalty):
        self.degs = degs
        self.waits = waits
        self.penalty = penalty

    def move(self, brick, ports, count):
        deg = self.degs[count]
        rotate1(brick, ports, deg)
        time.sleep(self.waits[count])

def are_parallel(m1, m2):
    return abs(m1 // 3 - m2 // 3) == 3

class Robot:

    HOST0 = '00:16:53:40:CE:B6'
    HOST1 = '00:16:53:4A:BA:BA'

    SINGLE_MOTOR = MotorType(
        [0, 90, 180, -180, -90], [0, .079, .151, .151, .079], .007
    )
    DOUBLE_MOTOR = MotorType(
        [0, -54, -108, 108, 54], [0, .057, .104, .104, .057], .005
    )
   
    COUNT = [-1, -2, 1] 
    MOVE = [
        (0, ev3.PORT_A, SINGLE_MOTOR),
        (1, ev3.PORT_C + ev3.PORT_D, DOUBLE_MOTOR),
        (0, ev3.PORT_B + ev3.PORT_C, DOUBLE_MOTOR),
        (0, ev3.PORT_D, SINGLE_MOTOR),
        (1, ev3.PORT_A + ev3.PORT_B, DOUBLE_MOTOR)
    ]

    def __init__(self):
        self.bricks = [
            ev3.EV3(protocol='Usb', host=Robot.HOST0), ev3.EV3(protocol='Usb', host=Robot.HOST1)
        ]
        self.bricks[0].lock = threading.Lock()
        self.bricks[1].lock = threading.Lock()

    def move1(self, m):
        brick, ports, motor = Robot.MOVE[m // 3]
        brick = self.bricks[brick]
        motor.move(brick, ports, Robot.COUNT[m % 3])

    def move2(self, m1, m2):
        brick, ports1, arm1 = Robot.MOVE[m1 // 3]
        _, ports2, arm2 = Robot.MOVE[m2 // 3]
        count1 = Robot.COUNT[m1 % 3]
        count2 = Robot.COUNT[m2 % 3]
        wait = max(arm1.waits[count1], arm2.waits[count2])
        penalty = max(arm1.penalty, arm2.penalty)
        rotate2(self.bricks[brick], ports1, arm1.degs[count1], ports2, arm2.degs[count2])
        time.sleep(wait + penalty)

    def execute(self, sol):
        if len(sol) == 0:
            return

        sol1 = []
        axial = []

        i = 0
        while i < len(sol):
            if i < len(sol) - 1 and are_parallel(sol[i], sol[i + 1]):
                sol1.append((sol[i], sol[i + 1]))
                axial.append(True)
                i += 2
            else:
                sol1.append(sol[i])
                axial.append(False)
                i += 1

        print(len(sol1), sol1)
        for i in range(len(sol1)):
            tick = time.time()
            if axial[i]:
                self.move2(sol1[i][0], sol1[i][1])
            else:
                self.move1(sol1[i])
            print(time.time() - tick)

