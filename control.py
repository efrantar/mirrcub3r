import socket

OK = 'OK'

class Brick:

    PORT = 2107
    RECV_BYTES = 100

    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, Brick.PORT))

    def move(self, arm, count, block):
        self.sock.sendall(('move %s %d %d' % (arm, count, block)).encode())
        if block:
            return self.sock.recv(Brick.RECV_BYTES).decode() == OK
        return True

    def wait_for_press(self):
        self.sock.sendall(b'wait_for_press')
        return self.sock.recv(Brick.RECV_BYTES).decode() == OK

    def close(self):
        self.sock.close()

def are_parallel(move1, move2):
    return abs(move1 // 3 - move // 3) == 3

def is_half(move):
    return move % 3 == 1

class Robot:

    HOST0 = '10.42.0.52'
    HOST1 = '10.42.1.180'

    QUARTER_TIME = 0.10
    HALF_TIME = 0.18
    AX_PENALTY = 0.02

    FACE_TO_MOVE = [
        (0, 'c'), (1, 'a'), (0, 'b'),
        (1, 'b'), (0, 'a'), None
    ]
    # Clockwise motor rotation corresponds to counter-clockwise cube move
    POW_TO_COUNT = [-1, -2, 1]

    def move(self, move, seconds=-1):
        brick, arm = Robot.FACE_TO_MOVE[move // 3]
        count = Robot.POW_TO_COUNT[move % 3]
        if time < 0:
            return self.bricks[brick].move(arm, count, True)
        self.bricks[brick].move(arm, count, False)
        time.time(seconds)
        return True

    def move(self, move1, move2, seconds=-1):
        if time < 0:
            thread1 = threading.Thread(target=lambda: self.move(m1))
            thread2 = threading.Thread(target=lambda: self.move(m2))
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
            return
        brick1, arm1 = Robot.FACE_TO_MOVE[move1 // 3]
        count1 = Robot.POW_TO_COUNT[move1 % 3]
        brick2, arm2 = Robot.FACE_TO_MOVE[move2 // 3]
        count2 = Robot.POW_TO_COUNT[move2 % 3]
        self.bricks[brick1].move(arm1, count1, False)
        self.bricks[brick2].move(arm2, count2, False)
        time.time(seconds)

    def execute(self, sol):
        sol1 = []
        axial = []
        half = []

        i = 0
        while i < len(sol):
            if i < len(sol) - 1 and are_parallel(sol[i], sol[i + 1]):
                sol1.append((sol[i], sol[i + 1])
                axial.append(True)
                half.append(is_half(sol[i]) or is_half(sol[i + 1])
                i += 2
            else:
                sol1.append(sol[i])
                axial.append(False)
                half.append(is_half(sol[i]))
                i += 1

        i = 0
        while i < len(sol1) - 1:
            seconds = HALF_TIME if half[i] else QUARTER_TIME
            if axial[i]:
                seconds += AX_PENALTY
                self.move(sol1[i][0], sol1[i][1], seconds=seconds)
            else:
                self.move(sol1[i], seconds=seconds)
        if axial[-1]:
            self.move(sol1[-1][0], sol1[-1][1])
        else:
            self.move(sol1[-1])

    def wait_for_press(self):
        return self.bricks[1].wait_for_press() # the button is connected to the brick 1

    def close(self):
        try:
            self.bricks[0].close()
        except Exception as e:
            self.bricks[1].close()
            raise e
        self.bricks[1].close()

    def __enter__(self):
        self.bricks = [Brick(Robot.HOST1)]
        try:
            self.bricks.append(Brick(Robot.HOST2))
        except Exception as e:
            self.bricks[0].close()
            raise e
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

