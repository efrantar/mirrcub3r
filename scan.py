from collections import namedtuple
import copy
import cv2
from heapq import *
import numpy as np
import urllib.request

N_COLORS = 6
N_EDGES = 12
N_CORNERS = 8
N_FACELETS = 54

NO_COL = -1
U = 0
R = 1
F = 2
D = 3
L = 4
B = 5

COL_NAMES = ['U', 'R', 'F', 'D', 'L', 'B']

URF = 0
UFL = 1
ULB = 2
UBR = 3
DFR = 4
DLF = 5
DBL = 6
DRB = 7

UR = 0
UF = 1
UL = 2
UB = 3
DR = 4
DF = 5
DL = 6
DB = 7
FR = 8
FL = 9
BL = 10
BR = 11

COLORS = ['blue', 'yellow', 'red', 'green', 'white', 'orange']

FACELET_TO_CUBIE = [
    ULB, UB, UBR, UL, -1, UR, UFL, UF, URF,
    URF, UR, UBR, FR, -1, BR, DFR, DR, DRB,
    UFL, UF, URF, FL, -1, FR, DLF, DF, DFR,
    DLF, DF, DFR, DL, -1, DR, DBL, DB, DRB,
    ULB, UL, UFL, BL, -1, FL, DBL, DL, DLF,
    UBR, UB, ULB, BR, -1, BL, DRB, DB, DBL 
]
FACELET_TO_POS = [
    0, 0, 0, 0, -1, 0, 0, 0, 0,
    1, 1, 2, 1, -1, 1, 2, 1, 1,
    1, 1, 2, 0, -1, 0, 2, 1, 1,
    0, 0, 0, 0, -1, 0, 0, 0, 0,
    1, 1, 2, 1, -1, 1, 2, 1, 1,
    1, 1, 2, 0, -1, 0, 2, 1, 1
]

CORNER_TWISTS = {
    (U, R, F), (U, F, L), (U, L, B), (U, B, R),
    (D, F, R), (D, L, F), (D, B, L), (D, R, B)
}
for c in list(CORNER_TWISTS):
    CORNER_TWISTS.add((c[1], c[2], c[0]))
    CORNER_TWISTS.add((c[2], c[0], c[1]))

CENTERS = [4, 13, 22, 31, 40, 49]
BOTTOM_FACE = [i for i in range(18, 27)]


def remove(l, e):
    try:
        l.remove(e)
    except:
        pass


class ColorMatcher:

    HUE_SHIFT = 30

    def match(self, bgrs):
        self.facecube = [NO_COL] * N_FACELETS
        for i in range(6):
            self.facecube[9 * i + 4] = i
        self.ecols = [[NO_COL] * 2 for _ in range(N_EDGES)]
        self.ccols = [[NO_COL] * 3 for _ in range(N_CORNERS)]

        self.eavail = [U, R, F, D, L, B] * 4
        self.eavail_part = [
            {R, L, F, B},
            {B, F, U, D},
            {U, D, R, L},
            {R, L, F, B},
            {U, D, F, B},
            {U, D, R, L}
        ]
        self.cavail = copy.deepcopy(self.eavail)
        self.cavail_part = copy.deepcopy(self.eavail_part)

        hsvs = cv2.cvtColor(np.expand_dims(bgrs, 0), cv2.COLOR_BGR2HSV)[0, :, :]
        hsvs[:, 0] = (hsvs[:, 0] + ColorMatcher.HUE_SHIFT) % 180
        by_hue = [f for f in np.argsort(hsvs[:, 0]) if f not in CENTERS]
        by_sat = [f for f in np.argsort(hsvs[:, 1]) if f not in CENTERS]
        by_val = [f for f in np.argsort(hsvs[:, 2]) if f not in CENTERS]

        # Find white facelets
        whites = []
        for f in by_sat:
            if f not in by_hue[-8:] and f not in by_val[:8]:
                self.assign(f, L)
                whites.append(f)
            if len(whites) == 8:
                break
        by_hue = np.array([i for i in by_hue if i not in whites])
 
        # Assign blue
        for f in by_hue[-8:]:
            self.assign(f, U)

        # Assign green and yellow
        for i in range(8):
            f = by_hue[16 + i]
            if not self.assign(f, R):
                self.assign(f, D)
            f = by_hue[31 - i]
            if not self.assign(f, D):
                self.assign(f, R)

        # Assign red and orange
        for i in range(8):
            f = by_hue[i]
            if not self.assign(f, F):
                self.assign(f, B)
            f = by_hue[15 - i]
            if not self.assign(f, B):
                self.assign(f, F)

        return ''.join([COL_NAMES[c] for c in self.facecube])

    def assign(self, facelet, col):
        if self.facecube[facelet] != NO_COL:
            return True

        cubie = FACELET_TO_CUBIE[facelet]
        if (facelet % 9) % 2 == 1:
            if col not in self.edge_cols(cubie):
                # print('elim', facelet, COLORS[col])
                return False
            self.assign_edge(facelet, col)
        else:
            if col not in self.corner_cols(cubie):
                # print('elim', facelet, COLORS[col])
                return False
            self.assign_corner(facelet, col)
        
        # print('assign', facelet, COLORS[col])
        return True

    def assign_edge(self, facelet, col):
        edge = FACELET_TO_CUBIE[facelet]
        self.ecols[edge][FACELET_TO_POS[facelet]]

        remove(self.eavail, col)
        if col not in self.eavail:
            for e in range(N_COLORS):
                remove(self.eavail_part[e], col)
        if len([c for c in self.ecols[edge] if c != NO_COL]) == 2:
            c1, c2 = self.ecols[edge]
            remove(self.eavail[c1], c2)
            remove(self.eavail[c2], c1)

        self.facecube[facelet] = col

    def assign_corner(self, facelet, col):
        corner = FACELET_TO_CUBIE[facelet]
        self.ccols[corner][FACELET_TO_POS[facelet]]

        remove(self.cavail, col)
        if col not in self.cavail:
            for c in range(N_COLORS):
                remove(self.cavail_part[c], col)
        if len([c for c in self.ccols[corner] if c != NO_COL]) <= 2:
            for c1 in range(3):
                if c1 != NO_COL:
                    for c2 in range(3):
                        remove(self.cavail_part[c1], c2)

        self.facecube[facelet] = col

    def edge_cols(self, edge):
        if self.ecols[edge][0] != NO_COL:
            return self.eavail_part[self.ecols[edge][0]]
        if self.ecols[edge][1] != NO_COL:
            return self.eavail_part[self.ecols[edge][1]]
        return self.eavail

    def corner_cols(self, corner):
        avail = {}
        count = 0
        i_missing = -1
        for i, c in enumerate(self.ccols[corner]):
            if c != NO_COL:
                avail |= self.cavail_part[c]
                count += 1
            elif i_missing < 0:
                i_missing = i

        if count == 1:
            return avail
        if count == 2:
            avail1 = []
            for c in avail:
                tmp = copy.copy(self.ccols[corner])
                tmp[i_missing] = c
                if tmp in CORNER_TWISTS:
                    avail1.append(c)
            return avail1

        return self.cavail


class ColorExtractor:

    def __init__(self, points, size):
        self.points = points
        self.size = size

    def extract_bgrs(self, image):
        d = self.size // 2
        scans = np.zeros((self.points.shape[0], 3), dtype=np.uint8)
        for i in range(self.points.shape[0]):
            x, y = self.points[i]
            tmp = image[(y - d):(y + d), (x - d):(x + d), :]
            scans[i, :] = np.median(tmp, axis=(0, 1))
        return scans


class IpCam:

    def __init__(self, url):
        self.url = url

    def frame(self):
        frame = urllib.request.urlopen(self.url)
        frame = np.array(bytearray(frame.read()), dtype=np.uint8)
        frame = cv2.imdecode(frame, -1) # choose encoding automatically -> default: BGR
        return frame


if __name__ == '__main__':
    import pickle
    points = np.array(pickle.load(open('scan-pos.pkl', 'rb')))
   
    cam = IpCam('http://192.168.178.25:8080/shot.jpg')
    image = cam.frame()
    cv2.imwrite('scan.jpg', image)
 
    extractor = ColorExtractor(points, 10)
    image = cv2.imread('scan.jpg')
    scans = extractor.extract_bgrs(image)

    hsvs = cv2.cvtColor(np.expand_dims(scans, 0), cv2.COLOR_BGR2HSV)[0, :, :]
    from mpl_toolkits.mplot3d import Axes3D 
    import matplotlib.pyplot as plt
    from matplotlib.colors import hsv_to_rgb
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(N_FACELETS):
        if i in CENTERS:
            continue
        ax.scatter(
            hsvs[i, 0], hsvs[i, 1], hsvs[i, 2], marker='o', 
            color=scans[i, ::-1] / 255
        )
    ax.set_xlabel('H')
    ax.set_ylabel('S')
    ax.set_zlabel('V')
    plt.show()

    matcher = ColorMatcher()
    import time
    tick = time.time()
    scans = extractor.extract_bgrs(image)
    facecube = matcher.match(scans)
    print(facecube)
    print(time.time() - tick)
    if facecube == '':
        exit()

    from solve import Solver
    with Solver() as solver:
        print(solver.solve(facecube))

