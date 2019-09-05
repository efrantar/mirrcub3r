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

    while True:
        print('Ready.')
        # robot.wait_for_press()
        input()
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
            print('Done! %fs' % (time.time() - start))
        else:
            print('Error.')

