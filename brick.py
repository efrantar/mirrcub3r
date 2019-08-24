#!/usr/bin/env python3

import socket
from ev3dev2.motor import *
from ev3dev2.sensor.lego import *

SPEED = SpeedPercent(100)

PORT = 2107
RECV_BYTES = 100
OK = 'OK'
ERROR = 'Error'

class Arm:

    DEGREES = [90, 180]

    def __init__(self, port):
        self.motor = MediumMotor(port)
        self.motor.stop_action = 'brake'
        self.pos = self.motor.position # resetting to 0 sometimes causes motor-movement ...

    def move(self, count, block):
        deg = Arm.DEGREES[abs(count) - 1] * (-1 if count < 0 else 1)
        self.pos += deg
        self.motor.on_to_position(SPEED, self.pos, block=block)

arms = {}
for port in ['a', 'b', 'c', 'd']:
    try:
        arm = Arm('out' + port.upper())
        arms[port] = arm
        print('Initialized arm on port %s.' % port)
    except:
        pass

button = None
try:
    button = TouchSensor()
    print('Start button ready.')
except:
    pass

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.bind(('0.0.0.0', PORT))
    sock.listen()
    print('Socket up.')

    running = True
    while running:
        print('Waiting for connection ...')
        conn, _ = sock.accept()
        print('Connected.')

        def send(msg):
            conn.sendall(msg.encode())
            print('Sent: "%s"' % msg)

        try:
            with conn:
                while running:
                    request = conn.recv(RECV_BYTES).decode()
                    print('Received: "%s"' % request)
                    if request == 'shutdown':
                        running = False
                        break
                    elif request == 'ping':
                        send(OK)
                    elif request == 'wait_for_press' and button is not None:
                        button.wait_for_pressed()
                        send(OK)
                    elif request.startswith('move '):
                        try:
                            splits = request.split(' ')
                            arms[splits[1]].move(int(splits[2]), bool(int(splits[3])))
                            send(OK)
                        except:
                            send(ERROR)
                    else:
                        send(ERROR)
        except:
            pass
        print('Connection closed.')

print('Socket closed.')

