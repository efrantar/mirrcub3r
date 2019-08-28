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

# Translates direction and degrees according to gearing
def translate(deg, gearing):
    if gearing is None:
        return deg
    # Make sure we get precise integer numbers if gearing ratio allows it
    return (-deg * gearing[1]) / gearing[0]

class Arm:

    SPEED = SpeedPercent(100) # we always want to run at max speed
    DEGREES = [0, 90, 180, -180, -90] # so that we can index directly for all possible counts

    def __init__(self, port, gearing=None):
        self.motor = MediumMotor(port)
        self.motor.stop_action = 'brake' # gets by far the best accurracy
        self.gearing = gearing

    def translate(self, deg):
        if self.gear1 == 1:
            return deg
        return -deg * self.gear1 / self.gear2

    def move(self, count, early=0):
        deg = translate(Arm.DEGREES[count], self.gearing)
        early = abs(translate(early, self.gearing)) # easier if this is always positive

        # Simply use a standard blocking move as it could otherwise cause infinite loops
        if early == 0:
            self.motor.on_for_degrees(Arm.SPEED, deg)
            return

        if deg < 0:
            ret = self.motor.position + deg + early # `deg < 0`
        else:
            ret = self.motor.position + deg - early

        self.motor.on_for_degrees(Arm.SPEED, deg, block=False)

        if deg < 0:
            while self.motor.position > ret:
                pass
        else:
            while self.motor.position < ret:
                pass

profile = sys.argv[1]
if profile == 'rd':
    ARMS = [('a', GEARING), ('b', GEARING)]
elif profile == 'ufl':
    ARMS = [('a', GEARING), ('b', None), ('c', GEARING)]
else:
    print('Unsupported profile "%s"' % profile)
    exit(0)

arms = {}
for port, gearing in ARMS:
    try:
        arm = Arm('out' + port.upper(), gearing)
        arms[port] = arm
        print('Initialized arm on port %s.' % port)
    except:
        print('Error initializing arm on port %s.' % port)
        exit(0)

# TODO: we want to support multiple buttons in the future
button = None
try:
    button = TouchSensor()
    print('Start button ready.')
except:
    pass

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

