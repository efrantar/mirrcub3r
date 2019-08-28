import socket
import threading
import time

OK = 'OK'

class Brick:

    PORT = 2107
    RECV_BYTES = 100

    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # We want to avoid any extra transmission delay
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.connect((host, Brick.PORT))

    def move(self, arm, count, early):
        self.sock.sendall(('move %s %d %d' % (arm, count, early)).encode())
        return self.sock.recv(Brick.RECV_BYTES).decode() == OK

    def wait_for_press(self):
        self.sock.sendall(b'wait_for_press')
        return self.sock.recv(Brick.RECV_BYTES).decode() == OK
    
    def ping(self):
        self.sock.sendall(b'ping')
        return self.sock.recv(Brick.RECV_BYTES).decode() == OK

    def close(self):
        self.sock.close()

def are_parallel(move1, move2):
    return abs(move1 // 3 - move2 // 3) == 3

def is_half(move):
    return move % 3 == 1

def clock(move):
    return move % 3 <= 1 # TODO: for now all half-turns are considered to be clockwise

CUT = 0
ANTICUT = 1
AX_CUT = 2
AX_PARTCUT = 3
AX_ANTICUT = 4
AXAX_CUT = 5
AXAX_PARTCUT = 6
AXAX_ANTICUT = 7

def cut(m1, m2):
    if isinstance(m1, int) and isinstance(m2, tuple):
        return cut(m2, m1)
    if isinstance(m1, tuple) and isinstance(m2, tuple):
        return max(cut(m1, m2[0]), cut(m1, m2[1])) + 3

    if isinstance(m1, int):
        return CUT if clock(m1) != clock(m2) else ANTICUT

    m11, m12 = m1
    clock1 = clock(m11)
    clock2 = clock(m12)

    if is_half(m11):
        if not is_half(m12):
            return CUT if clock1 != clock(m2) else ANTICUT
    else:
        if is_half(m12):
            return CUT if clock2 != clock(m2) else ANTICUT

    if clock1 == clock2:
        return AX_CUT if clock1 != clock(m2) else AX_ANTICUT
    return AX_PARTCUT

def is_f(m):
    return m // 3 == 2

class Robot:

    HOST0 = '10.42.1.52'
    HOST1 = '10.42.0.180'

    EARLY_CUT = [
        15,
        10,
        15,
        1, 
        5,
        15,
        0,
        1
    ]

    FACE_TO_MOVE = [
        (0, 'c'), (1, 'a'), (0, 'b'),
        (1, 'b'), (0, 'a'), None
    ]
    # Clockwise motor rotation corresponds to counter-clockwise cube move
    POW_TO_COUNT = [-1, -2, 1]

    def move1(self, move, early=0):
        brick, arm = Robot.FACE_TO_MOVE[move // 3]
        count = Robot.POW_TO_COUNT[move % 3]
        return self.bricks[brick].move(arm, count, early)

    def move2(self, move1, move2, early=0):
        thread1 = threading.Thread(target=lambda: self.move1(move1, early))
        thread2 = threading.Thread(target=lambda: self.move1(move2, early))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
    def execute(self, sol):
        if len(sol) == 0:
            return

        sol1 = []
        axial = []
        half = []

        i = 0
        while i < len(sol):
            if i < len(sol) - 1 and are_parallel(sol[i], sol[i + 1]):
                sol1.append((sol[i], sol[i + 1]))
                axial.append(True)
                half.append(is_half(sol[i]) or is_half(sol[i + 1]))
                i += 2
            else:
                sol1.append(sol[i])
                axial.append(False)
                half.append(is_half(sol[i]))
                i += 1

        for i in range(len(sol1) - 1):
            tick = time.time()
            print(sol1[i])
            cut1 = cut(sol1[i], sol1[i + 1])
            early = Robot.EARLY_CUT[cut1]
            print(early)
            if axial[i]:
                self.move2(sol1[i][0], sol1[i][1], early=early)
            else:
                self.move1(sol1[i], early=early)
            print(time.time() - tick)
        if axial[-1]:
            self.move2(sol1[-1][0], sol1[-1][1])
        else:
            self.move1(sol1[-1])

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
        self.bricks = [Brick(Robot.HOST0)]
        try:
            self.bricks.append(Brick(Robot.HOST1))
        except Exception as e:
            self.bricks[0].close()
            raise e
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

