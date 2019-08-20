import cv2
import numpy as np
import os
import urllib.request

WIDTH = 1080
HEIGHT = 1920

N_STICKERS = 54

class IpCam:

    def __init__(self, url):
        self.url = url

    def frame(self):
        frame = urllib.request.urlopen(self.url)
        frame = np.array(bytearray(frame.read()), dtype=np.uint8)
        frame = cv2.imdecode(frame, -1) # choose encoding automatically -> default: BGR
        return frame

class CubeScanner:

    SHIFT = 30

    def __init__(self, polys, order, n_percol):
        self.order = order
        self.n_percol = n_percol
        
        self.masks = [None] * N_STICKERS
        for i in range(N_STICKERS):
            mask = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
            for j in np.where(order == i)[0]:
                cv2.fillPoly(mask, np.array([polys[j]], dtype=np.int32), 255)
            if np.sum(order == i) > 0: # don't store masks for positions we don't scan
                self.masks[i] = mask

    def scan(self, image):
        # Simpler to do for the full image than after every masking
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Rotate circular hue space so that red always has low hue values
        image[:, :, 0] = (image[:, :, 0] + CubeScanner.SHIFT) % 180

        test = np.zeros((1920, 1080, 3), np.uint8)

        scans = np.full((N_STICKERS, 3), -1) # invalid positions have invalid value
        for i in range(N_STICKERS):
            if self.masks[i] is not None:
                scans[i, :] = np.median(image[self.masks[i] > 0], axis=0)
                
                tmp = np.full((1920, 1080, 3), scans[i, :], dtype=np.uint8)
                tmp = cv2.bitwise_and(tmp, tmp, mask=self.masks[i])
                tmp = cv2.cvtColor(tmp, cv2.COLOR_HSV2BGR)
                test = cv2.bitwise_or(test, tmp)

        cv2.imwrite('test.jpg', test)

        import matplotlib.pyplot as plt
        from matplotlib.colors import hsv_to_rgb

        for i in range(len(scans)):
            if scans[i, 0] >= 0:
                plt.plot(scans[i, 1], scans[i, 2], 'o', color=hsv_to_rgb([
                    ((scans[i, 0] - 30) % 180) / 180., scans[i, 1] / 255., scans[i, 2] / 255.
                ]))
        plt.xlabel('saturation')
        plt.ylabel('value')

        test1 = (2./3. * scans[:, 1] + 1./3. * (255 - scans[:, 2])).argsort()
        plt.plot(scans[test1[:8], 1], scans[test1[:8], 2], 'or')
        plt.savefig('plot.png')

        colors = np.zeros(N_STICKERS, dtype=np.int) # white defaults to 0
        

        # White has low value and high saturation
        tmp = 2./3. * scans[:, 1] + 1./3. * (255 - scans[:, 2])
        asc_hue = np.argsort(scans[:, 0])[(N_STICKERS - 6 * self.n_percol):] # drop invalid positions
        asc_hue = asc_hue[~np.in1d(asc_hue, np.argsort(tmp)[:self.n_percol])] # drop white
        print(scans[asc_hue, :])
        for i in range(0, len(asc_hue), self.n_percol):
            colors[asc_hue[i:(i + self.n_percol)]] = i // self.n_percol + 1

        return colors

import pickle
points, order = pickle.load(open('scan-setup.pkl', 'rb'))
order = np.array([i for i, _ in order])
for i in range(len(order)):
    order[i] += order[i] // 8 + int(order[i] % 8 >= 4)

import time
tick = time.time()
scanner = CubeScanner(points, order, 8)
colors = scanner.scan(cv2.imread('sample.jpg'))
print(time.time() - tick)

from solve import *
with Solver() as solver:
    SCAN_ORDER = [5, 3, 1, 4, 0, 2]
    SCAN_COLOR = ['L', 'F', 'B', 'R', 'D', 'U']
    # SCAN_COLOR = ['W', 'R', 'O', 'Y', 'G', 'B']

    for f in range(6):
        colors[9 * f + 4] = SCAN_ORDER[f]
    facecube = ''.join([SCAN_COLOR[c] for c in colors])
    print(facecube)

    print(solver.solve(facecube))

