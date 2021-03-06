# Main program controlling the robot; not much is happening here, we just call the appropriate
# tools implemented in the other files.

from configparser import ConfigParser
import pickle
import subprocess
import threading
import time
from threading import Thread

import numpy as np

from control import *
from scan import *
from solve import *

config = ConfigParser()
config.read('config')
config = config['DEFAULT']

with Solver() as solver:
    print('Solver initialized.')

    robot = Robot()
    print('Connected to robot.')

    points = np.array(pickle.load(open(config['pos'], 'rb')))
    extractor = ColorExtractor(points, int(config['scan_size']))
    matcher = ColorMatcher()
    cam = IpCam(config['cam'])
    print('Scanning set up.')

    flash = False

    print('Ready.') # we don't want to print this again and again while waiting for button presses
    while True: # polling is the most straight-forward way to check both buttons at once
        time.sleep(.05) # 50ms should be sufficient for a smooth experience
        if robot.scramble_pressed():
            scramble = solver.scramble()
            start = time.time()
            robot.execute(scramble)
            print('Scrambled! %fs' % (time.time() - start))
            cam.flash(False)
            flash = False
            continue
        elif not robot.solve_pressed():
            continue
        else:
            if not flash:
                cam.flash(True)
                flash = True
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
            # Turn off flash only after processor is not busy with solving anymore
            flash_off = Thread(target=lambda: cam.flash(False)) 
            flash_off.start()

            print('Executing ...')
            robot.execute(sol)
            print('Solved! %fs' % (time.time() - start))
            
            flash_off.join()
            flash = False
        else:
            print('Error.')
            
        print('Ready.')

