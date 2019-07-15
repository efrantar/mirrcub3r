# TODO: optimal corner cutting correction for 2-moves

import socket

class Brick:

    PORT = 2107
    RECV_BYTES = 100

    def __init__(self, host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, Brick.PORT)

    def move(self, arm, count, speed_percent):
        sock.sendall(b'move %s %d %d' % (arm, count, speed_percent))
        return sock.recv(Brick.RECV_BYTES).decode() == 'OK'

    def reset(self, arm):
        sock.sendall(b'reset %s' % arm)
        return sock.recv(Brick.RECV_BYTES).decode() == 'OK'

    def close(self):
        self.sock.close()

# TODO: handle second brick
class Robot:

    HOST1 = '10.42.0.138'
    HOST2 = ''

    SPEED_PERCENT = 50
    AXIS_TO_MOVE = [
        (0, 'c'), (0, 'b'), (1, 'a'),
        (1, 'b'), (0, 'a'), None
    ]

    def move(self, move):
        brick, arm = Robot.AXIS_TO_MOVE[move / 3]
        count = [1, 2, -1][move % 3]
        return self.bricks[brick].move(arm, count, SPEED_PERCENT)

    def reset(self):
        for brick, arm in AXIS_TO_MOVE:
            if brick == 1:
                continue
            if not self.bricks[brick].reset(arm):
                return False
        return True

    def close(self):
        self.bricks[0].close()

    def __enter__(self):
        self.bricks = [Brick(Robot.HOST1), None]
        return self

    def __exit__(self):
        self.close()

