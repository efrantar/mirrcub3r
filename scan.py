import numpy as np
import cv2 as cv

import urllib.request
import os
import time


class IpCam:

    def __init__(self, url):
        self.url = url

    def frame(self):
        frame = urllib.request.urlopen(self.url)
        frame = np.array(bytearray(frame.read()), dtype=np.uint8)
        frame = cv.imdecode(frame, -1) # choose encoding automatically -> default: BGR
        return frame


class FileCam:

    def __init__(self, path):
        self.path = path
        self.image = 0

    def frame(self):
        frame = cv.imread(self.path + ('/%d.jpg' % self.image))
        self.image += 1
        return frame


class ImageSaver:

    def __init__(self, cam, path):
        self.cam = cam
        self.path = path
        self.image = 0

    def frame(self):
        frame = self.cam.frame()
        cv.imwrite(self.path + ('/%d.jpg' % self.image), frame)
        self.image += 1
        return frame


class CubeScanner:

    # Shift color space so that red is always the smallest
    SHIFT = 30

    def __init__(self, cam, schedule, positions, size2, per_col=9):
        self.cam = cam
        self.schedule = schedule
        self.positions = positions
        self.size2 = size2
        self.per_col = per_col
        
        self.step = 0
        # Makes sure that skipped positions will have max value after shifting
        self.scans = np.full((len(schedule), 3), 180 - SHIFT)

    def next(self):
        frame = cam.frame()
        for pos in np.where(self.schedule == self.step)[0]:
            x, y = self.positions[pos, :]
            self.scans[pos, :] = np.mean(
                cv.cvtColor(
                    frame[(y - self.size2):(y + self.size2), (x - self.size2):(x + self.size2), :], 
                    cv.COLOR_BGR2HSV
                ), axis=(0, 1)
            )
        self.step += 1

    def finish(self):
        colors = np.zeros(len(self.schedule), dtype=np.int) # white defaults to 0
        asc_hue = np.argsort((self.scans[:, 0] + SHIFT) % 181) # max value is 180
        for i, pos in enumerate(
            asc_hue[
                # Skip white positions
                ~np.in1d(asc_hue, np.argsort(self.scans[:, 1])[:self.per_col])
            ][:-((9 - self.per_col) * 6)] # Ignore skipped positions (they will have max value)
        ):
            colors[pos] = i // self.per_col + 1
        return colors
                
    def complete(self):
        return self.step > np.max(self.schedule)


def test_data():
    cam = IpCam('http://192.168.1.2:8080/shot.jpg')
    cam = ImageSaver(cam, 'scans/' + time.strftime('%Y%m%d%H%M%S'))
    os.mkdir(cam.path)

    for i in range(6):
        input()
        cam.frame()
        print(i + 1)


def draw_positions(image, positions, size2):
    for x, y in positions:
        cv.rectangle(image, (x - SIZE2, y - SIZE2), (x + SIZE2, y + SIZE2), (0, 0, 0))
    return image


SCHEDULE_TEST = np.array([i // 9 if i % 9 != 4 else -1 for i in range(54)])
 
STEP = 300
POS_GRID = [[(175 + STEP * j, 625 + STEP * i) for j in range(3)] for i in range(3)]

POSITIONS_TEST = np.full((54, 2), -1)
for i in range(6):
    for j in range(9):
        if j != 4:
            POSITIONS_TEST[9 * i + j, :] = POS_GRID[j // 3][j % 3]

cam = FileCam('scans/20180609113719')
scanner = CubeScanner(cam, SCHEDULE_TEST, POSITIONS_TEST, 50, per_col=8)

while not scanner.complete():
    scanner.next()
colors = scanner.finish()
colors[[4, 13, 22, 31, 40, 49]] = (1, 5, 2, 4, 0, 3)

NUM_TO_COL = ['W', 'R', 'O', 'Y', 'G', 'B']
for i in range(6):
    for j in range(3):
        for k in range(3):
            print(NUM_TO_COL[colors[9 * i + 3 * j + k]], end='')
        print()
    print()

