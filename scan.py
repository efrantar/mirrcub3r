# This file implements the color recognition.

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

# To do the constraint matching we have to repeat several defintions from
# C++ solving algorithm here.

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

# Map a facelet to the cubie it is on
FACELET_TO_CUBIE = [
    ULB, UB, UBR, UL, -1, UR, UFL, UF, URF,
    URF, UR, UBR, FR, -1, BR, DFR, DR, DRB,
    UFL, UF, URF, FL, -1, FR, DLF, DF, DFR,
    DLF, DF, DFR, DL, -1, DR, DBL, DB, DRB,
    ULB, UL, UFL, BL, -1, FL, DBL, DL, DLF,
    UBR, UB, ULB, BR, -1, BL, DRB, DB, DBL 
]
# Map a facelet to the position within its cubie
FACELET_TO_POS = [
    0, 0, 0, 0, -1, 0, 0, 0, 0,
    1, 1, 2, 1, -1, 1, 2, 1, 1,
    1, 1, 2, 0, -1, 0, 2, 1, 1,
    0, 0, 0, 0, -1, 0, 0, 0, 0,
    1, 1, 2, 1, -1, 1, 2, 1, 1,
    1, 1, 2, 0, -1, 0, 2, 1, 1
]

# Generate all possible twisted configurations of the corners
CORNER_TWISTS = {
    (U, R, F), (U, F, L), (U, L, B), (U, B, R),
    (D, F, R), (D, L, F), (D, B, L), (D, R, B)
}
for c in list(CORNER_TWISTS):
    CORNER_TWISTS.add((c[1], c[2], c[0]))
    CORNER_TWISTS.add((c[2], c[0], c[1]))

CENTERS = [4, 13, 22, 31, 40, 49]
BOTTOM_FACE = [i for i in range(18, 27)]


# `remove()` that does not throw if the element does not exist
def remove(l, e):
    try:
        l.remove(e)
    except:
        pass


# Matches the scanned BGR-values to cube colors.

# Getting this to work at least somewhat decently with the robot's mirrors is extremely tricky
# as there are varying viewing angles and lighting conditions depending on which exactly
# facelet we are trying to match. Thus most usually very effective conventional
# methods (i.e. clustering, matching to reference values while considering constraints, etc.)
# unfortunately do not seem to work. We resort here to a combination of constraint matching
# and HSV sorting with some additional rather ad-hoc tricks. While this method is certainly
# not the most elegant, it seems to be surprisingly robust and works much better than
# anything else we have tried.
class ColorMatcher:

    # Due to the hue-space being circular red can have both very high and very low values.
    # To avoid any problems caused by this we simply shift the space by 30 degrees.
    HUE_SHIFT = 30

    def match(self, bgrs):
        self.facecube = [NO_COL] * N_FACELETS
        for i in range(6): # hard-code the center-facelets as they are locked for our robot
            self.facecube[9 * i + 4] = i
        self.ecols = [[NO_COL] * 2 for _ in range(N_EDGES)]
        self.ccols = [[NO_COL] * 3 for _ in range(N_CORNERS)]

        self.eavail = [U, R, F, D, L, B] * 4
        self.eavail_part = [
            [R, L, F, B],
            [B, F, U, D],
            [U, D, R, L],
            [R, L, F, B],
            [U, D, F, B],
            [U, D, R, L]
        ]
        self.cavail = copy.deepcopy(self.eavail)
        self.cavail_part = [avail * 2 for avail in self.eavail_part]

        hsvs = cv2.cvtColor(np.expand_dims(bgrs, 0), cv2.COLOR_BGR2HSV)[0, :, :]
        hsvs[:, 0] = (hsvs[:, 0] + ColorMatcher.HUE_SHIFT) % 180
        # Note that the input also contains scans for the centers to make indexing more
        # straight-forward but we don't want them to confuse the color matching and thus filter
        # them out at this point.
        by_hue = [f for f in np.argsort(hsvs[:, 0]) if f not in CENTERS]
        by_sat = [f for f in np.argsort(hsvs[:, 1]) if f not in CENTERS]
        by_val = [f for f in np.argsort(hsvs[:, 2]) if f not in CENTERS]

        # The whole process highly depends on us correctly matching all white facelets a priori
        whites = []
        for f in by_sat: # white is recognized by a low saturation value
            # The most common incorrect assignments happen with a blue scan (high hue) or some
            # other very dark color (low val), just filtering those out seems to make finding the 
            # white facelets surprising consitent.
            if f not in by_hue[-8:] and f not in by_val[:8]:
                self.assign(f, L)
                whites.append(f)
            if len(whites) == 8:
                break
        # Now proceed white the hue ordering of all remaining colors
        by_hue = np.array([i for i in by_hue if i not in whites])
 
        # Assign blue; this is typically very consitent we should not be making any errors here
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

        # Finally match red and orange; a few errors are quite common here, however they can
        # usually be corrected by the constraints imposed via all the previously matched colors;
        # Note also that we assign from outside to in, i.e. the most distinct colors first and
        # easiest to confuse ones last
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
        if (facelet % 9) % 2 == 1: # is on an edge
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
        if col not in self.eavail: # maximum number of edge facelets with a color reached
            for e in range(N_COLORS):
                remove(self.eavail_part[e], col)
        if len([c for c in self.ecols[edge] if c != NO_COL]) == 2: # edge fully assigned
            c1, c2 = self.ecols[edge]
            remove(self.eavail_part[c1], c2)
            remove(self.eavail_part[c2], c1)

        self.facecube[facelet] = col

    def assign_corner(self, facelet, col):
        corner = FACELET_TO_CUBIE[facelet]
        self.ccols[corner][FACELET_TO_POS[facelet]]

        remove(self.cavail, col)
        if col not in self.cavail: # maximum corner facelets with some color found
            for c in range(N_COLORS):
                remove(self.cavail_part[c], col)
        for c in range(3): # when we have more than 1 color of a corner
            if c != NO_COL and c != col:
                remove(self.cavail_part[col], c)
                remove(self.cavail_part[c], col)

        self.facecube[facelet] = col

    def edge_cols(self, edge):
        # If an edge already has one color simply return its available partners
        if self.ecols[edge][0] != NO_COL:
            return self.eavail_part[self.ecols[edge][0]]
        if self.ecols[edge][1] != NO_COL:
            return self.eavail_part[self.ecols[edge][1]]
        return self.eavail

    def corner_cols(self, corner):
        avail = set([c for c in range(N_COLORS)])
        count = 0
        i_missing = -1
        for i, c in enumerate(self.ccols[corner]):
            if c != NO_COL:
                avail &= set(self.cavail_part[c])
                count += 1
            elif i_missing < 0:
                i_missing = i

        if count == 1:
            return avail
        if count == 2: # use corner twists to limit the valid colors even more
            avail1 = []
            for c in avail:
                tmp = copy.copy(self.ccols[corner])
                tmp[i_missing] = c
                if tmp in CORNER_TWISTS:
                    avail1.append(c)
            return avail1

        return self.cavail


# Extracts average BGR value of small squares around the given scan-points
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


# Very simple interface to fetch an image from the "IPWebCam" app
class IpCam:

    def __init__(self, url):
        self.url = url

    def frame(self):
        frame = urllib.request.urlopen(self.url)
        frame = np.array(bytearray(frame.read()), dtype=np.uint8)
        frame = cv2.imdecode(frame, -1) # choose encoding automatically -> default: BGR
        return frame


# Testing/experimentation code (mostly to try out color recognition without having to launch the robot)
if __name__ == '__main__':
    import pickle
    points = np.array(pickle.load(open('scan-pos.pkl', 'rb')))
   
    # cam = IpCam('http://192.168.178.25:8080/shot.jpg')
    # image = cam.frame()
    # cv2.imwrite('scan.jpg', image)
 
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

