# This file implements the cubie level of the twophase solver.
# It defines constants for the cubies, the basic cubie level cube moves and the coordinates. It also contains a class
# `CubieCube` with methods for performing cubie moves and calculating as well as reconstructing coordinates.


# Definitions of corners and edges. The orders matter for the coordinate calculations.

N_CORNERS = 8

URF = 0
UFL = 1
ULB = 2
UBR = 3
DFR = 4
DLF = 5
DBL = 6
DRB = 7

N_EDGES = 12

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


# Multiplies permutation `p1` with permutation `p2`.
def _mul(p1, p2):
    p3 = [-1] * len(p1)
    for i in range(len(p1)):
        p3[i] = p1[p2[i]]
    return p3

# Indicators for selecting whether to multiply corners or edges.
CORNERS = 0
EDGES = 1

# Map of indicators defined above to functions that multiply the corners/edges of `CubieCube`s `c1` and `c2`.
_MUL = [
    lambda c1, c2: c1._mul_corners(c2), # CORNERS
    lambda c1, c2: c1._mul_edges(c2) # EDGES
]


# Coordinate indicators.
TWIST = 0
FLIP = 1
FRBR = 2
URFDLF = 3
URUL = 4
UBDF = 5
URDF = 6
PAR = 7


# TYPE 1 COORDINATES. Used for `TWIST` and `FLIP`.
# The last parameter element is omitted from the encoding to avoid empty/invalid table entries.

# Encodes array `a` as a type 1 coordinate using basis `basis`.
def _encode1(a, basis):
    c = 0
    for i in a[:-1]: # don't encode last element
        c = basis * c + i
    return c

# Reconstructs `a` from type 1 coordinate `c` using basis `basis`.
def _decode1(c, a, basis):
    par = 0
    for i in range(len(a) - 2, -1, -1): # skip last element
        a[i] = c % basis
        par += a[i]
        c //= basis
    a[len(a) - 1] = (basis - (par % basis)) % basis # reconstruct last element (ignored by loop) from `par`

# TYPE 2 COORDINATES. Used for `FRBR`, `URFDLF`, `URUL`, `UBDF` and `URDF`.

# The parameter `l0` specifies which configuration of cubies maps to an position coordinate of 0. If `l0=True`, then
# 0 orientation means that all cubies in `elems` occupy the `len(p)` leftmost spots of `p`, for `l0=False` it are the
# rightmost. This is extremly important to save table space, as in phase 2 the position part of the `FRBR` coordinate
# is 0 since the edges occupy all the rightmost entries. As a direct consequence the edges considered by `URDF` can
# also never be in those positions. This means `l0=False` for `FRBR` and `l0=True` for `URDF`.

# Encodes perumtation `p` as a type 2 coordinate considering the elements in `elems` and the counting given by `l0`.
def _encode2(p, elems, l0):
    p1 = [-1] * len(elems) # the order of `elems` in `p` is saved here to the compute the permutation coordinate

    # Calculate the position coordinate `c1`.
    c1 = 0
    if l0:
        j = 0 # index into `p1`
        for i in range(len(p)):
            if p[i] in elems:
                c1 += CNK[i][j+1]
                p1[j] = p[i]
                j += 1
    else:
        j = len(elems) - 1
        for i in range(len(p)):
            if p[i] in elems:
                c1 += CNK[len(p) - 1 - i][j + 1]
                p1[len(elems) - 1 - j] = p[i]
                j -= 1

    # Calculate the location coordinate `c2`.
    c2 = 0
    for i in range(len(elems) - 1, 0, -1): # we can skip 0 as `p1` is already properly sorted at that point
        cnt = 0 # number of rotations necessary so that `p1[i] = elems[i]`
        while p1[i] != elems[i]:
            # Left rotate the first `i` elements in `p` by 1.
            tmp = p1[0]
            for j in range(i):
                p1[j] = p1[j+1]
            p1[i] = tmp
            cnt += 1
        c2 = (c2 + cnt) * i

    return FAC[len(elems)] * c1 + c2 # finally merge both coordinates

# Reconstructs `p` from type 2 coordinate `c` considering the elements in `elems` and the counting given by `l0`.
def _decode2(c, p, elems, l0):
    elems = list(elems)  # we don't want to mess up `elems` as there will be passed global constants
    # However, we do want to modify the passed `p`.
    for i in range(len(p)):
        p[i] = -1

    c1 = c // FAC[len(elems)]
    c2 = c % FAC[len(elems)]

    # Reconstruct permutation.
    for i in range(1, len(elems)): # we can skip position 0 as the permutation is already reconstructed at that point
        cnt = c2 % (i + 1) # number of rotations to do to reconstruct cubie `i` of the permutation
        for _ in range(cnt):
            # Right rotate the first `i` elements in `p` by 1.
            tmp = elems[i]
            for j in range(i, 0, -1):
                elems[j] = elems[j-1]
            elems[0] = tmp
        c2 //= (i + 1)

    # Reconstruct positions.
    j = len(elems) - 1
    for i in (range(len(p), -1, -1) if l0 else range(len(p))):
        tmp = CNK[i if l0 else (len(p) - 1 - i)][j + 1] # just saved so that it does not need to be recalculated
        if c1 - tmp >= 0:
            p[i] = elems[j if l0 else (len(elems) - 1 - j)]
            c1 -= tmp
            j -= 1


# Computes the parity of permutation `p`.
def _parity(p):
    par = 0
    for i in range(len(p)):
        for j in range(i):
            if p[j] > p[i]:
                par += 1
    return par & 1


# Maximum values for corner and edge orientation. Defined as public as they are also used in other files.
MAX_CO = 2
MAX_EO = 1

# Lists of cubies tracked by their corresponding coordinates.
_FRBR_EDGES = [FR, FL, BL, BR]
_URFDLF_CORNERS = [URF, UFL, ULB, UBR, DFR, DLF]
_URUL_EDGES = [UR, UF, UL]
_UBDF_EDGES = [UB, DR, DF]
_URDF_EDGES = _URUL_EDGES + _UBDF_EDGES

# Map of coordinate indicators to functions calculating this coordinate for a `CubieCube` `c`.
# Note that `l0` does not matter for `URFDLF`, `URUL` and `UBDF` and is chose to use the simpler version.
_GET = [
    lambda c: _encode1(c.co, MAX_CO + 1), # TWIST
    lambda c: _encode1(c.eo, MAX_EO + 1), # FLIP
    lambda c: _encode2(c.ep, _FRBR_EDGES, False), # FRBR
    lambda c: _encode2(c.cp, _URFDLF_CORNERS, True), # URFDLF
    lambda c: _encode2(c.ep, _URUL_EDGES, True), # URUL
    lambda c: _encode2(c.ep, _UBDF_EDGES, True), # UBDF
    lambda c: _encode2(c.ep, _URDF_EDGES, True), # URDF
    lambda c: _parity(c.cp) # PAR
]

# Map of coordinate indicators to functions calculating this coordinate for a `CubieCube` `c`
_SET = [
    lambda c, v: _decode1(v, c.co, MAX_CO + 1), # TWIST
    lambda c, v: _decode1(v, c.eo, MAX_EO + 1), # FLIP
    lambda c, v: _decode2(v, c.ep, _FRBR_EDGES, False), # FRBR
    lambda c, v: _decode2(v, c.cp, _URFDLF_CORNERS, True), # URFDLF
    lambda c, v: _decode2(v, c.ep, _URUL_EDGES, True), # URUL
    lambda c, v: _decode2(v, c.ep, _UBDF_EDGES, True), # UBDF
    lambda c, v: _decode2(v, c.ep, _URDF_EDGES, True) # URDF
    # we don't need a setter for `par` as its move-table is hardcoded
]


# Merges an `URUL` coordinate and a `UBDF` coordinate to a `URDF` coordinate.
def merge_urdf(urul, ubdf):
    c1 = CubieCube.make_solved()
    c1.set_coord(URUL, urul)
    c2 = CubieCube.make_solved()
    c2.set_coord(UBDF, ubdf)

    for i in range(N_EDGES - len(_FRBR_EDGES)): # this is only called in phase two where the last 4 edges are fixed
        if c2.ep[i] in _UBDF_EDGES:
            if c1.ep[i] != -1: # collision
                return -1 # return -1 as otherwise `get_coord(URDF)` might run into an infinite loop
            c1.ep[i] = c2.ep[i]

    return c1.get_coord(URDF)


# Represents a cube at cubie level. Provides methods for making cubie moves as well as getting and setting coordinates.
class CubieCube:

    # Returns a new `CubieCubie` with the given cubie perumtations and orientations.
    @staticmethod
    def make(cp, co, ep, eo):
        c = CubieCube()
        c.cp = cp # corner permutation
        c.co = co # corner orientations
        c.ep = ep # edge permutation
        c.eo = eo # edge orientations
        return c

    # Returns a `CubieCube` in solved state.
    @staticmethod
    def make_solved():
        return CubieCube.make(
            [i for i in range(N_CORNERS)], [0] * N_CORNERS,
            [i for i in range(N_EDGES)], [0] * N_EDGES
        )

    # Multiplies the corners with the `CubieCube` `other`.
    def _mul_corners(self, other):
        self.cp = _mul(self.cp, other.cp)
        self.co = [(self.co[other.cp[i]] + other.co[i]) % 3 for i in range(N_CORNERS)]

    # Multiplies the edges with the `CubieCube` `other`.
    def _mul_edges(self, other):
        self.ep = _mul(self.ep, other.ep)
        self.eo = [(self.eo[other.ep[i]] + other.eo[i]) & 1 for i in range(N_EDGES)]

    # Multiplies the corners/edges as indicated by `mul` with the `CubieCube` `other`.
    def mul(self, mul, other):
        _MUL[mul](self, other)


    # Computes the coordinate `coord`.
    def get_coord(self, coord):
        return _GET[coord](self)

    # Reconstructs the cube from the `coord` coordinate with value `v`
    def set_coord(self, coord, v):
        return _SET[coord](self, v)

    # Checks the cube for solvability.
    def check(self):
        # Check if all corners/edges are present and their orientations have a valid sum.
        if any(i not in self.cp for i in range(N_CORNERS)) or sum(self.co) % 3 != 0:
            return False
        if any(i not in self.ep for i in range(N_EDGES)) or sum(self.eo) & 1 != 0:
            return False
        return _parity(self.cp) == _parity(self.ep) # edge and corner parities must match


# Definition of cube moves in form of `CubieCube`s.
MOVES = [
    CubieCube.make(
        [UBR, URF, UFL, ULB, DFR, DLF, DBL, DRB], [0] * N_CORNERS,
        [UB, UR, UF, UL, DR, DF, DL, DB, FR, FL, BL, BR], [0] * N_EDGES
    ), # U
    CubieCube.make(
        [DFR, UFL, ULB, URF, DRB, DLF, DBL, UBR], [2, 0, 0, 1, 1, 0, 0, 2],
        [FR, UF, UL, UB, BR, DF, DL, DB, DR, FL, BL, UR], [0] * N_EDGES
    ), # R
    CubieCube.make(
        [UFL, DLF, ULB, UBR, URF, DFR, DBL, DRB], [1, 2, 0, 0, 2, 1, 0, 0],
        [UR, FL, UL, UB, DR, FR, DL, DB, UF, DF, BL, BR], [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0]
    ), # F
    CubieCube.make(
        [URF, UFL, ULB, UBR, DLF, DBL, DRB, DFR], [0] * N_CORNERS,
        [UR, UF, UL, UB, DF, DL, DB, DR, FR, FL, BL, BR], [0] * N_EDGES
    ), # D
    CubieCube.make(
        [URF, ULB, DBL, UBR, DFR, UFL, DLF, DRB], [0, 1, 2, 0, 0, 2, 1, 0],
        [UR, UF, BL, UB, DR, DF, FL, DB, FR, UL, DL, BR], [0] * N_EDGES
    ), # L
    CubieCube.make(
        [URF, UFL, UBR, DRB, DFR, DLF, ULB, DBL], [0, 0, 1, 2, 0, 0, 2, 1],
        [UR, UF, UL, BR, DR, DF, DL, BL, FR, FL, UB, DB], [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1]
    ) # B
]


# Precompute factorials.  We compute them up to `N_EDGES` just to be safe.
FAC = [1]
for i in range(N_EDGES):
    FAC.append(FAC[i] * (i+1))

# Precompute binomials. `N_EDGES` is again a safe maximum.
# Note that this is in general not a good way to compute binomials, but for small numbers it is the easiest.
CNK = [
    # Returning 0 if `k > n` is critical for properly handling type 2 coordinates.
    [FAC[n] / (FAC[k] * FAC[n-k]) if k <= n else 0 for k in range(N_EDGES + 1)] \
        for n in range(N_EDGES + 1)
]
