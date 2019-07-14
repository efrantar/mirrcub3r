#!/usr/bin/env python3

import socket
from ev3dev2.motor import *

PORT = 2107

class Arm:

    DEGREES = [90, 180]

    def __init__(self, port):
        self.motor = MediumMotor(port)
        self.motor.stop_action = 'brake'
        self.reset()

    def move(self, count, speed_percent):
        deg = Arm.DEGREES[abs(count) - 1] * (-1 if count < 0 else 1)
        self.pos += deg
        self.motor.on_to_position(SpeedPercent(speed_percent), self.pos)

    def reset(self):
        self.motor.position = 0
        self.pos = 0

def handle_action(action):
    try:
        splits = request.split(' ')
        if splits[1] not in arms:
            return False

        if splits[0] == 'move':
            arms[splits[1]].move(int(splits[2]), int(splits[3]))
            return True
        elif splits[0] == 'reset':
            arms[splits[1]].reset()
            return True
    except:
        pass
    return False

arms = {}
for port in ['a', 'b', 'c', 'd']:
    try:
        arm = Arm('out' + port.upper())
        arms[port] = arm
        print('Initialized arm on port %s.' % port)
    except:
        pass

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', PORT))
    sock.listen()
    print('Socket up.')

    running = True
    while running:
        print('Waiting for connection ...')
        conn, _ = sock.accept()
        print('Connected.')

        with conn:
            while running:
                request = conn.recv(100).decode()
                print('Received: "%s"' % request)
                if request == 'shutdown':
                    running = False
                    break
                elif handle_action(request):
                    conn.sendall(b'OK')
                    print('Sent: "%s"' % 'OK')
                else:
                    conn.sendall(b'Error')
                    print('Sent: "%s"' % 'Error')
        print('Connection closed.')

print('Socket closed.')

