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
                # Since almost all pixels are 0, it is faster to access the non-zero ones via their index
                self.masks[i] = np.where(mask > 0)

    def scan(self, image):
        colors = np.zeros(N_STICKERS, dtype=np.int) # white defaults to 0
       
        # Make sure that invalid positions have values that will never bother us in any calculations
        scans = np.tile(np.array([[-1, 255, 0]]), (N_STICKERS, 1))
        for i in range(N_STICKERS):
            if self.masks[i] is not None:
                # Faster to convert only the relevant pixels to HSV
                tmp = cv2.cvtColor(np.expand_dims(image[self.masks[i]], 0), cv2.COLOR_BGR2HSV) # input needs to be 3D
                # Rotate circular hue space such that red always has low values
                tmp[:, :, 0] = (tmp[:, :, 0] + 30) % 180
                scans[i, :] = np.median(tmp, axis=(0, 1)) # median for better robustness

        # White has low value and high saturation
        tmp = 2./3. * scans[:, 1] + 1./3. * (255 - scans[:, 2])
        asc_hue = np.argsort(scans[:, 0])[(N_STICKERS - 6 * self.n_percol):] # drop invalid positions
        asc_hue = asc_hue[~np.in1d(asc_hue, np.argsort(tmp)[:self.n_percol])] # drop white
 
        for i in range(0, len(asc_hue), self.n_percol):
            colors[asc_hue[i:(i + self.n_percol)]] = i // self.n_percol + 1

        return colors

if __name__ == '__main__':
    import pickle
    points, order = pickle.load(open('scan-setup.pkl', 'rb'))
    order = np.array([i for i, _ in order])
    for i in range(len(order)):
        order[i] += order[i] // 8 + int(order[i] % 8 >= 4)

    cam = IpCam('http://192.168.178.25:8080/shot.jpg')
    image = cam.frame()
    # cv2.imwrite('check.jpg', image)
    # image = cv2.imread('sample.jpg')

    import time
    scanner = CubeScanner(points, order, 8)
    tick = time.time()
    colors = scanner.scan(image)
    print(time.time() - tick)

    print(colors)

    from solve import *
    with Solver() as solver:
        SCAN_ORDER = [5, 3, 1, 4, 0, 2]
        SCAN_COLOR = ['L', 'F', 'B', 'R', 'D', 'U']

        for f in range(6):
            colors[9 * f + 4] = SCAN_ORDER[f]
        facecube = ''.join([SCAN_COLOR[c] for c in colors])
        print(facecube)

        print(solver.solve(facecube))

