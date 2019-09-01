#!/usr/bin/env python3

import sys
import socket
from ev3dev2.motor import *
from ev3dev2.sensor.lego import *

PORT = 2107
RECV_BYTES = 100
OK = 'OK'
ERROR = 'Error'

GEARING = (40, 24)

class SingleMotor:

    def __init__(self, port, deg90=90):
        self.motor = MediumMotor(port)
        self.motor.speed_sp = self.motor.max_speed
        self.motor.stop_action = 'hold' # other modes completely unusable
        # Open files to minimize any delays later
        self.motor.position
        self.motor.stop() # open the `command` file

    @property
    def position(self):
        return self.motor.position

    @property
    def position_sp(self):
        return self.motor.position_sp

    @position_sp.setter
    def position_sp(self, position_sp):
        self.motor.position_sp = position_sp

    def run_to_abs_pos(self):
        self.motor.run_to_abs_pos()

class DoubleMotor:

    def __init__(self, port1, port2):
        self.motor1 = SingleMotor(port1)
        self.motor2 = SingleMotor(port2)

    @property
    def position(self):
        # We rely on the fact that the gears are always aligned and minimize file accesses
        return self.motor1.position

    @property
    def position_sp(self):
        return self.motor1.position_sp

    @position_sp.setter
    def position_sp(self, position_sp):
        self.motor1.position_sp = position_sp
        self.motor2.position_sp = position_sp

    def run_to_abs_pos(self):
        self.motor1.run_to_abs_pos()
        self.motor2.run_to_abs_pos()

# Translates direction and degrees according to gearing
def translate(deg, gearing):
    if gearing is None:
        return deg
    # Make sure we get precise integer numbers if gearing ratio allows it
    return (-deg * gearing[1]) / gearing[0]

class Arm:

    DEGREES = [0, 90, 180, -180, -90] # so that we can index directly for all possible counts

    def __init__(self, motor, gearing=None):
        self.motor = motor
        self.gearing = gearing
        self.pos = motor.position

        # Ideal position should always be a perfectly aligned cube
        deg90 = abs(translate(90, gearing))
        pos = abs(self.pos)
        pos = pos // deg90 * deg90 if pos % deg90 < deg90 / 2 else (pos // deg90 + 1) * deg90
        self.pos = pos * (-1 if self.pos < 0 else 1)

    def move(self, count, early):
        cur = self.motor.position # just a single file read for setup
        deg = translate(Arm.DEGREES[count], self.gearing)
        early = abs(translate(early, self.gearing)) # easier if this is always positive
        # Apply correction if we are not perfectly aligned
        ret = cur + (self.pos - cur) + deg + (early if deg < 0 else -early)
        self.pos += deg

        self.motor.position_sp = self.pos
        self.motor.run_to_abs_pos()

        if deg < 0:
            while self.motor.position > ret:
                pass
        else:
            while self.motor.position < ret:
                pass

arms = {}
button = None

profile = sys.argv[1]
if profile == 'rd':
    arms['a'] = Arm(SingleMotor('outA'), None)
    arms['b'] = Arm(SingleMotor('outB'), None)
    button = TouchSensor() # simply auto-detect
elif profile == 'ufl':
    arms['a'] = Arm(SingleMotor('outA'), None)
    arms['b'] = Arm(DoubleMotor('outB', 'outC'), GEARING)
    arms['c'] = Arm(SingleMotor('outD'), None)
else:
    print('Unsupported profile "%s"' % profile)
    exit(0)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Avoid annoying "Address already in use"
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # We want as little delay as possible
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    # Bind to all interfaces
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

        try:
            with conn: # debug `print()`s actually increase latency noticeably
                while running:
                    request = conn.recv(RECV_BYTES).decode()
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
                            arms[splits[1]].move(int(splits[2]), int(splits[3]))
                            send(OK)
                        except:
                            send(ERROR)
                    else:
                        send(ERROR)
        except:
            pass
        print('Connection closed.')

print('Socket closed.')

