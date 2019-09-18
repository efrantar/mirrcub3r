import pickle
import subprocess
import threading
import time

import numpy as np

from control import *
from scan import *
from solve import *

CAM_URL = 'http://192.168.178.25:8080/shot.jpg'

SCAN_ORDER = [5, 3, 1, 4, 0, 2]
SCAN_COLOR = ['L', 'F', 'B', 'R', 'D', 'U']

with Solver() as solver:
    print('Solver initialized.')

    robot = Robot()
    print('Connected to robot.')

    points, order = pickle.load(open('scan-setup.pkl', 'rb'))
    order = np.array([i for i, _ in order])
    for i in range(len(order)):
        order[i] += order[i] // 8 + int(order[i] % 8 >= 4)
    scanner = CubeScanner(points, order, 8)

    cam = IpCam(CAM_URL)
    print('Scanner set up.')

    print('Ready.') # we don't want to print this again and again while waiting for button presses
    while True:
        time.sleep(.05) # 50ms should be sufficient for a smooth experience
        if robot.scramble_pressed():
            scramble = solver.scramble()
            start = time.time()
            robot.execute(scramble)
            print('Scrambled! %fs' % (time.time() - start))
            continue
        elif not robot.solve_pressed():
            continue
        # Now actually start solving

        frame = cam.frame()
        start = time.time()

        print('Scanning ...')
        colors = scanner.scan(frame)
        for f in range(6):
            colors[9 * f + 4] = SCAN_ORDER[f]
        facecube = ''.join([SCAN_COLOR[c] for c in colors])

        print('Solving ...')
        sol = solver.solve(facecube)

        if sol is not None:
            print('Executing ...')
            robot.execute(sol)
            print('Solved! %fs' % (time.time() - start))
        else:
            print('Error.')
        print('Ready.')

