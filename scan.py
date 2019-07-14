import numpy as np
import cv2 as cv

import os
import urllib.request


class IpCam:

    def __init__(self, url):
        self.url = url

    def frame(self):
        frame = urllib.request.urlopen(self.url)
        frame = np.array(bytearray(frame.read()), dtype=np.uint8)
        frame = cv.imdecode(frame, -1) # choose encoding automatically -> default: BGR
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
        self.scans = np.full((len(schedule), 3), 180 - CubeScanner.SHIFT)

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
        asc_hue = np.argsort((self.scans[:, 0] + CubeScanner.SHIFT) % 181) # max value is 180
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

