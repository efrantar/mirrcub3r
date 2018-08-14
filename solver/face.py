from cubie import CubieCube, MAX_CO, MAX_EO


N_COLORS = 6

U = 0
R = 1
F = 2
D = 3
L = 4
B = 5


COL = ['U', 'R', 'F', 'D', 'L', 'B'] # U, R, F, D, L, B
_N_PIECES = 9

def _cubelet(c):
    return [c[i] * _N_PIECES + c[i+1] - 1 for i in range(0, len(c), 2)]

_CORNLETS = [
    _cubelet(c) for c in [
        (U,9,R,1,F,3), (U,7,F,1,L,3), (U,1,L,1,B,3), (U,3,B,1,R,3), (D,3,F,9,R,7), (D,1,L,9,F,7), (D,7,B,9,L,7),
        (D,9,R,9,B,7)
    ]
] # URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB

_EDGELETS = [
    _cubelet(c) for c in [
        (U,6,R,2), (U,8,F,2), (U,4,L,2), (U,2,B,2), (D,6,R,8), (D,2,F,8), (D,4,L,8), (D,8,B,8), (F,6,R,4), (F,4,L,6),
        (B,6,L,4), (B,4,R,6)
    ]
] # UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR

def _encode(p, i=0):
    c = 0
    for j in range(len(p)):
        c = N_COLORS * c + p[(j-i) % len(p)] # i=1 is a clockwise rotation, i=2 a counter-clockwise one
    return c

_CORNERS = {
    _encode(c, j): (i, j) \
    for i, c in enumerate([(U,R,F), (U,F,L), (U,L,B), (U,B,R), (D,F,R), (D,L,F), (D,B,L), (D,R,B)]) \
        for j in range(MAX_CO + 1)
}

_EDGES = {
    _encode(e, j): (i, j)
    for i, e in enumerate([(U,R), (U,F), (U,L), (U,B), (D,R), (D,F), (D,L), (D,B), (F,R), (F,L), (B,L), (B,R)])
        for j in range(MAX_EO + 1)
}

# Taken from Kociemba.
#
#             |************|
#             |*U1**U2**U3*|
#             |************|
#             |*U4**U5**U6*|
#             |************|
#             |*U7**U8**U9*|
#             |************|
# ************|************|************|************|
# *L1**L2**L3*|*F1**F2**F3*|*R1**R2**F3*|*B1**B2**B3*|
# ************|************|************|************|
# *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*|
# ************|************|************|************|
# *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*|
# ************|************|************|************|
#             |************|
#             |*D1**D2**D3*|
#             |************|
#             |*D4**D5**D6*|
#             |************|
#             |*D7**D8**D9*|
#             |************|
#
# Face-order: U, R, F, D, L, B

def face_to_cubie(s):
    try:
        f = map(lambda c: COL.index(c), s)
        cc = CubieCube.make_solved()

        for i, c in enumerate(_CORNLETS):
            cc.cp[i], cc.co[i] = _CORNERS[_encode([f[j] for j in c])]
        for i, e in enumerate(_EDGELETS):
            cc.ep[i], cc.eo[i] = _EDGES[_encode([f[j] for j in e])]

        return cc
    except: # a bit hacky, but does the job well enough here
        pass
