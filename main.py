# Main program controlling the robot; not much is happening here, we just call the appropriate
# tools implemented in the other files.

import pickle
import subprocess
import threading
import time

import numpy as np

from control import *
from scan import *
from solve import *

# Fortunately, this seems to stay rather consistent
CAM_URL = 'http://192.168.178.25:8080/shot.jpg'

with Solver() as solver:
    print('Solver initialized.')

    robot = Robot()
    print('Connected to robot.')

    points = np.array(pickle.load(open('scan-pos.pkl', 'rb')))
    extractor = ColorExtractor(points, 10)
    matcher = ColorMatcher()
    cam = IpCam(CAM_URL)
    print('Scanning set up.')

    print('Ready.') # we don't want to print this again and again while waiting for button presses
    while True: # polling is the most straight-forward way to check both buttons at once
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
        # NOTE: We start timing only after we have received a frame from the camera and start any processing.
        # While this might not be 100% conform to the Guiness World Record rules, I am (at least at this point)
        # not interested in optimizing the camera latency as I do not think this should be an integral part
        # of a cube-solving robot.
        start = time.time()
        print('Scanning ...')
        scans = extractor.extract_bgrs(frame)
        facecube = matcher.match(scans)
        print('Solving ...')
        sol = solver.solve(facecube)
        print(time.time() - start)

        if sol is not None:
            print('Executing ...')
            robot.execute(sol)
            print('Solved! %fs' % (time.time() - start))
        else:
            print('Error.')
        print('Ready.')

