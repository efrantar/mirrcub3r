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

BOTTOM_FACELETS = [i for i in range(18, 27)]

HUE_SHIFT = 30
RED_H = -10 + HUE_SHIFT
ORANGE_H = 10 + HUE_SHIFT
YELLOW_H = 30 + HUE_SHIFT
GREEN_H = 60 + HUE_SHIFT
BLUE_H = 120 + HUE_SHIFT
WHITE_S = 0

def remove(l, e):
    try:
        l.remove(e)
    except:
        pass


Assignment = namedtuple('Assignment', ['facelet', 'col'])

class ColorMatcher:

    def match(self, scans):
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

        # TODO: penalty for low V
        heap = []

        red_ord = np.argsort(np.abs(scans[:, 0] - RED_H))
        orange_ord = np.argsort(np.abs(scans[:, 0] - ORANGE_H))
        yellow_ord = np.argsort(np.abs(scans[:, 0] - YELLOW_H))
        green_ord = np.argsort(np.abs(scans[:, 0] - GREEN_H))
        blue_ord = np.argsort(np.abs(scans[:, 0] - BLUE_H))
        white_ord = np.argsort(np.abs(scans[:, 1] - WHITE_S))

        plot_cols(scans[red_ord])
        plot_cols(scans[orange_ord])
        # plot_cols(scans[yellow_ord])
        # plot_cols(scans[green_ord])
        # plot_cols(scans[blue_ord])
        # plot_cols(scans[white_ord])

        print(scans[19, :])

        for i in range(N_FACELETS):
            bot = 100 * int(blue_ord[i] in BOTTOM_FACELETS)  # match bottom face last
            heap.append((i + bot, Assignment(blue_ord[i], U))) 

        blue_pen = np.zeros(N_FACELETS)
        blue_pen[blue_ord[:9]] = np.arange(start=1, stop=10)
        tmp = blue_pen.copy()
        for i in range(N_FACELETS):
            tmp[white_ord[i]] += i
        tmp = np.argsort(tmp)
        white_pen = np.zeros(N_FACELETS)
        white_pen[white_ord[:9]] = np.arange(start=1, stop=10)

        def add(i, ord, pen, col):
            bot = 100 * int(ord[i] in BOTTOM_FACELETS)
            heap.append((i + bot + pen[ord[i]], Assignment(ord[i], col)))

        for i in range(N_FACELETS):
            add(i, white_ord, blue_pen, L)
            add(i, red_ord, white_pen, F)
            add(i, orange_ord, white_pen, B)
            add(i, yellow_ord, white_pen, R)
            add(i, green_ord, white_pen, D)

        heapify(heap)
        matched = 6 # center facelets are hardcoded
        while matched < N_FACELETS:
            if len(heap) == 0:
                return ''
            _, ass = heappop(heap)
            cubie = FACELET_TO_CUBIE[ass.facelet]

            if self.facecube[ass.facelet] != NO_COL:
                continue
            if (ass.facelet % 9) % 2 == 1: # edge
                if ass.col not in self.edge_cols(cubie):
                    print('elim_edge', ass.facelet, ass.col)
                    continue
                self.assign_edge(ass.facelet, ass.col)            
            else: # corner
                if ass.col not in self.corner_cols(cubie):
                    print('elim_corner', ass.facelet, ass.col)
                    continue    
                self.assign_corner(ass.facelet, ass.col)
            matched += 1

        return ''.join([COL_NAMES[c] for c in self.facecube])

    def assign_edge(self, facelet, col):
        print('assign_edge', facelet, ['blue', 'yellow', 'red', 'green', 'white', 'orange'][col])

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
        print('assign_corner', facelet, ['blue', 'yellow', 'red', 'green', 'white', 'orange'][col])

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

    def extract_hsv(self, image):
        d = self.size // 2
        scans = np.zeros((points.shape[0], 3), dtype=np.float)
        for i in range(points.shape[0]):
            x, y = self.points[i]
            tmp = cv2.cvtColor(image[(y - d):(y + d), (x - d):(x + d), :], cv2.COLOR_BGR2HSV)
            tmp[:, :, 0] = (tmp[:, :, 0] + HUE_SHIFT) % 180
            scans[i, :] = np.max(tmp, axis=(0, 1)) # median for better robustness
        return scans

    def extract_rgb(self, image):
        d = self.size // 2
        scans = np.zeros((points.shape[0], 3), dtype=np.float)
        for i in range(points.shape[0]):
            x, y = self.points[i]
            tmp = image[(y - d):(y + d), (x - d):(x + d), :]
            scans[i, :] = np.median(tmp, axis=(0, 1))[::-1]
        return scans / 255.

    def extract_lab(self, image):
        d = self.size // 2
        scans = np.zeros((points.shape[0], 3), dtype=np.float)
        for i in range(points.shape[0]):
            x, y = self.points[i]
            tmp = cv2.cvtColor(image[(y - d):(y + d), (x - d):(x + d), :], cv2.COLOR_BGR2Lab)
            scans[i, :] = np.median(tmp, axis=(0, 1))
        return scans / 255.


class IpCam:

    def __init__(self, url):
        self.url = url

    def frame(self):
        frame = urllib.request.urlopen(self.url)
        frame = np.array(bytearray(frame.read()), dtype=np.uint8)
        frame = cv2.imdecode(frame, -1) # choose encoding automatically -> default: BGR
        return frame


def plot_cols(scans):
    import matplotlib.pyplot as plt
    from matplotlib.colors import hsv_to_rgb
    for i in range(N_FACELETS):
        plt.plot(
            i, 0, 'o',
            color=hsv_to_rgb([((scans[i, 0] - 30) % 180) / 180, scans[i, 1] / 255, scans[i, 2] / 255])
        )
    plt.show()

if __name__ == '__main__':
    import pickle
    points = np.array(pickle.load(open('scan-pos.pkl', 'rb')))
   
    # cam = IpCam('http://192.168.178.25:8080/shot.jpg')
    # image = cam.frame()
    # cv2.imwrite('check.jpg', image)
 
    extractor = ColorExtractor(points, 10)
    image = cv2.imread('scan.jpg')
    import time
    tick = time.time()
    scans = extractor.extract_lab(image)
    print(scans)

    rgbs = extractor.extract_rgb(image)
    labs = extractor.extract_lab(image)

    from mpl_toolkits.mplot3d import Axes3D 
    import matplotlib.pyplot as plt
    from matplotlib.colors import hsv_to_rgb
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(N_FACELETS):
        ax.scatter(
            labs[i, 0], labs[i, 1], labs[i, 2], marker='o', 
            color=rgbs[i, :]
        )
    ax.set_xlabel('L')
    ax.set_ylabel('a')
    ax.set_zlabel('b')
    plt.show()

    import time
    matcher = ColorMatcher()
    facecube = matcher.match(scans)
    print(time.time() - tick)
    print(facecube)
    if facecube == '':
        exit()

    from solve import Solver
    with Solver() as solver:
        print(solver.solve(facecube))

