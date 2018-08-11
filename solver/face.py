from cubie import CubieCube, MAX_CO, MAX_EO


N_COLORS = 6

U = 0
R = 1
F = 2
D = 3
L = 4
B = 5


_CORNLETS = [
    (8,9,20), (6,18,38), (0,36,47), (2,45,11), (29,26,15), (27,44,24), (33,53,42), (35,17,51)
] # U9R1F3, U7F1L3, U1L1B3, U3B1R3, D3F9R7, D1L9F7, D7B9L7, D9R9B7

_EDGELETS = [
    (5,10), (7,19), (3,37), (1,46), (32,16), (28,25), (30,43), (34,52), (23,12), (21,41), (50,39), (48,14)
] # U6R2, U8F2, U4L2, U2B2, D6R8, D2F8, D4L8, D8B8, F6R4, F4L6, B6L4, B4R6

def _encode(p, i=0):
    c = 0
    for j in range(len(p)):
        c = N_COLORS * c + p[(j-i) % len(p)]
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

_COL = ['U', 'R', 'F', 'D', 'L', 'B'] # U, R, F, D, L, B

def face_to_cubie(s):
    try:
        f = map(lambda c: _COL.index(c), s)
        cc = CubieCube.make_solved()

        for i, c in enumerate(_CORNLETS):
            cc.cp[i], cc.co[i] = _CORNERS[_encode([f[j] for j in c])]
        for i, e in enumerate(_EDGELETS):
            cc.ep[i], cc.eo[i] = _EDGES[_encode([f[j] for j in e])]

        return cc
    except:
        pass
