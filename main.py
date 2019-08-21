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

    with Robot() as robot:
        print('Connected to robot.')

        points, order = pickle.load(open('scan-setup.pkl', 'rb'))
        order = np.array([i for i, _ in order])
        for i in range(len(order)):
            order[i] += order[i] // 8 + int(order[i] % 8 >= 4)
        scanner = CubeScanner(points, order, 8)

        cam = IpCam(CAM_URL)
        print('Scanner set up.')

        def run_parallel(m1, m2):
            thread1 = threading.Thread(target=lambda: robot.move(m1))
            thread2 = threading.Thread(target=lambda: robot.move(m2))
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()

        print('Ready.')
        robot.button()
        frame = cam.frame()

        print('Scanning ...')
        colors = scanner.scan(frame)
        start = time.time()
        for f in range(6):
            colors[9 * f + 4] = SCAN_ORDER[f]
        facecube = ''.join([SCAN_COLOR[c] for c in colors])

        print('Solving ...')
        sol = solver.solve(facecube)

        def opp_axes(m1, m2):
            tmp = m1 // 3 - m2 // 3
            return tmp == 0 or abs(tmp) == 3

        if sol is not None:
            print('Executing ...')
        
            i = 0
            while i < len(sol):
                if i < len(sol) - 1 and opp_axes(sol[i], sol[i + 1]):
                    run_parallel(sol[i], sol[i + 1])
                    i += 2
                else:
                    robot.move(sol[i])
                    i += 1

            print('Done! %fs' % (time.time() - start))
        else:
            print('Error.')

