import copy
from heapq import *

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
    UBL, UB, UBR, UL, -1, UR, ULF, UF, URF,
    URF, UR, UBR, FR, -1, RB, DFR, DR, DRB,
    UFL, UF, URF, FL, -1, FR, DLF, DF, DFR,
    DLF, DF, DFR, DL, -1, DR, DBL, DB, DRB,
    ULB, UL, UFL, BL, -1, FL, DBL, DL, DLF,
    UBR, UB, ULB, BR, -1, BL, DBR, DB, DBL 
]

CORNER_TWISTS = {
    (U, R, F), (U, F, L), (U, L, B), (U, B, R),
    (D, F, R), (D, L, F), (D, B, L), (D, R, B)
}
for c in list(CORNER_TWISTS):
    CORNER_TWISTS.add((c[1], c[2], c[0]))
    CORNER_TWISTS.add((c[2], c[0], c[1]))

def dist(col1, col2):
    return np.sum((col1 - col2) ** 2)

class MatchingFacelet:

    def __init__(self, i, lab, baselines):
        self.i = i
        self.dists = {col: dist(lab, b) for col, b in enumerate(baselines)}
        self.best = 0
        for col, dist in self.dists.items():
            if dist < self.dists[self.best]:
                self.best = col

    def next(self):
        self.dists.remove(self.best)
        self.best = NO_COLOR
        for col, dist in self.dists.items():
            if self.best == NO_COLOR or dist < self.dists[self.best]:
                self.best = col

class ColorMatcher:

    BASELINES = [
    ]

    def __init__(self, baselines=ColorMatcher.BASELINES):
        self.baselines = self.baselines

    def match(self, labs, fsched):
        self.facecube = [NO_COLOR] * N_FACELETS
        self.ecols = [[NO_COLOR] * 2 for _ in range(N_EDGES)]
        self.ccols = [[NO_COLOR] * 3 for _ in range(N_CORNERS)]

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

        mfs = [MatchingFacelet(i, labs[i], self.baselines) for i in range(N_FACELETS)]
        for facelets in fsched:
            heap = [(mfs[f].dists[mfs[f].best], f) in facelets]
            heapfiy(heap)

            while len(heap) > 0:
                mf = mfs[heappop(heap)[1]]
                
                if mf.best == NO_COLOR:
                    return []
                cubie = FACELET_TO_CUBIE[mf.i]
                if (mf.i % 9) % 2 == 1:
                    if mf.best not in self.edge_cols(cubie):
                        mf.next()
                        heappush(heap, (mf.dists[mf.best], mf.i))
                    self.assign_edge(mf.i, mf.best)
                else:
                    if mf.best not in self.corner_cols(cubie)
                        mf.next()
                        heappush(heap, (mf.dists[mf.best], mf.i))
                    self.assign_corner(mf.i, mf.best)

        for f in range(6):
            colors[9 * f + 4] = f
        return ''.join([COL_NAMES[c] for c in self.facecube])

    def assign_edge(facelet, col):
        edge = FACELET_TO_CUBIE[facelet]
        self.ecols[edge][FACELET_TO_POS[facelet]]

        self.eavail.remove(col)
        if col not in self.eavail:
            for e in range(N_COLORS):
                self.eavail_part.remove(col)
        if self.assigned(self.ecols[edge]) == 2:
            c1, c2 = self.ecols[edge]
            self.eavail[c1].remove(c2)
            self.eavail[c2].remove(c1)

        self.facecube[facelet] = col

    def assign_corner(facelet, col):
        corner = FACELET_TO_CUBIE[facelet]
        self.ccols[corner][FACELET_TO_POS[facelet]]

        self.cavail.remove(col)
        if col not in self.cavail:
            for c in range(N_COLORS):
                self.cavail_part[c].remove(col)
        if self.assigned(self.ccols[corner]) <= 2:
            for c1 in range(3):
                if c1 != NO_COL
                    for c2 in range(3):
                        self.cavail_part[c1].remove(c2)

        self.facecube[facelet] = col

    def edge_colors(edge):
        if self.ecols[edge][0] != NO_COL:
            return self.eavail_part[self.ecols[edge][0]]
        if self.ecols[edge][1] != NO_COL:
            return self.eavail_part[self.ecols[edge][1]]
        return self.eavail

    def corner_colors(corner):
        avail = {}
        assigned = 0
        i_missing = -1
        for i, c in enumerate(self.ccols[corner]):
            if c != NO_COL:
                avail |= self.cavail_part[c]
                assigned += 1
            else if i_missing < 0:
                i_missing = i

        if self.count(self.ccols[corner]) == 1:
            return avail
        if self.count(self.ccols[corner]) == 2:
            avail1 = []
            for c in avail:
                tmp = copy.copy(self.ccols[corner])
                tmp[i_missing] = c
                if tmp in CORNER_TWISTS:
                    avail1.append(c)
            return avail1

        return self.cavail

    def assigned(cols):
        return count(c for c in cols if c != NO_COL)

