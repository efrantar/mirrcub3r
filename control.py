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

CUT = 0
ANTICUT = 1
AX_CUT = 2
AX_ANTICUT = 3
AX_PARTCUT = 4

def are_parallel(move1, move2):
    return abs(move1 // 3 - move // 3) == 3

def cw(move):
    return move % 3 <= 1 # TODO: for now all double moves are clockwise

def is_double(move):
    return move % 3 == 1

# `m2` must not be an axial move. This is because we determine the
# corner-cutting individually for both parts of an axial move as they
# are not affected by each other.
def cut_type(m1, m2):
    # `m1` is a simple move
    if not ininstance(m1, int):
        return CUT if cw(m1) != cw(m2) else ANTICUT

    m11, m12 = m1 # `m1` is an axial move

    # When the axial move contains exactly one double move, this is the
    # same as if we are corner-cutting with just this double move. Note
    # that this can only be done because the double-move delay is longer
    # than the single-move axial anti-cut one anyways.
    if is_double(m11):
        if not is_double(m12):
            return CUT if cw(m11) != cw(m2) else ANTICUT
    else:
        if is_double(m12):
            return CUT if cw(m12) != cw(m2) else ANTICUT

    cw11 = cw(m11)
    cw12 = cw(m12)
    cw2 = cw(m2)

    if cw11 == cw12:
        return AX_CUT if cw11 != cw2 else AX_ANTICUT:
    return AX_PARTCUT # slice-moves will always be partial cuts

class Robot:

    HOST0 = '10.42.0.52'
    HOST1 = '10.42.1.180'

    FACE_TO_MOVE = [
        (0, 'c'), (1, 'a'), (0, 'b'),
        (1, 'b'), (0, 'a'), None
    ]
    # Clockwise motor rotation corresponds to counter-clockwise cube move
    POW_TO_COUNT = [-1, -2, 1]

    DELAYS = [
        [0.09, 0.19], # CUT
        [0.10, 0.20], # ANTICUT
        [0.09, 0.09], # AX_CUT
        [0.11, 0.21], # AX_ANTICUT
        [0.10, 0.20]  # AX_PARTCUT
    ] # TODO: just some initial guesses, further experimentation will be necessary

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
        i = 0
        while i < len(sol):
            if i < len(sol) - 1 and are_parallel(sol[i], sol[i + 1]):
                sol1.append((sol[i], sol[i + 1])
                axial.append(True)
                i += 2
            else:
                sol1.append(sol[i])
                axial.append(False)
                i += 1

        i = 0
        while i < len(sol1) - 1:
            pass

    def wait_for_press(self):
        self.bricks[1].wait_for_press() # the button is connected to the brick 1

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

