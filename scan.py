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
        self.scans = np.full((len(schedule), 3), -1) # invalid positions have invalid value

    def next(self):
        frame = self.cam.frame()
        
        for pos in np.where(self.schedule == self.step)[0]:
            x, y = self.positions[pos, :]
            roi = frame[(y - self.size2):(y + self.size2), (x - self.size2):(x + self.size2), :]
            self.scans[pos, :] = np.median(cv.cvtColor(roi, cv.COLOR_BGR2HSV), axis=(0, 1))
            self.scans[pos, 0] = (self.scans[pos, 0] + CubeScanner.SHIFT) % 180
        
        self.step += 1

    def finish(self):
        colors = np.zeros(len(self.schedule), dtype=np.int) # white defaults to 0
       
        # White has low value and high hue
        tmp = (self.scans[:, 1] + 255 - self.scans[:, 2]) / 2.
        asc_hue = np.argsort(self.scans[:, 0])[(54 - 6 * self.per_col):] # drop invalid positions
        asc_hue = asc_hue[~np.in1d(asc_hue, np.argsort(tmp)[:self.per_col])] # drop white
        for i in range(0, len(asc_hue), self.per_col):
            colors[asc_hue[i:(i + self.per_col)]] = i // self.per_col + 1
        
        return colors
                
    def complete(self):
        return self.step > np.max(self.schedule)

