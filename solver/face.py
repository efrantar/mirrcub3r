from cubie import CubieCube, _MAX_CO


N_COLORS = 6

U = 0
R = 1
F = 2
D = 3
L = 4
B = 5


_N_PIECES = 9
_P = {f + str(j): i * 3 + j for i, f in enumerate(['U', 'R', 'F', 'D', 'L', 'B']) for j in range(1, _N_PIECES+1)}

def _corner(p1, p2, p3):
    return _P[p1], _P[p2], _P[p3]

_CORNLETS = [
    _corner('U9','R1','F3'), _corner('U7','F1','L3'), _corner('U1','L1','B3'), _corner('U3','B1','R3'),
    _corner('D3','F9','R7'), _corner('D1','L9','F7'), _corner('D7','B9','L7'), _corner('D9','R9','B7')
]

def _edge(p1, p2):
    return _P[p1], _P[p2]

_EDGELETS = [
    _edge('U6','R2'), _edge('U8','F2'), _edge('U4','L2'), _edge('U2','B2'), _edge('D6','R8'), _edge('D2','F8'),
    _edge('D4','L8'), _edge('D8','B8'), _edge('F6','R4'), _edge('F4','L6'), _edge('B6','L4'), _edge('B4','R6')
]

# URF, UFL, ULB, UBR, DFR, DLF, DBL, DRB
_CORNERS = [(U,R,F), (U,F,L), (U,L,B), (U,B,R), (D,F,R), (D,L,F), (D,B,L), (D,R,B)]
# UR, UF, UL, UB, DR, DF, DL, DB, FR, FL, BL, BR
_EDGES = [(U,R), (U,F), (U,L), (U,B), (D,R), (D,F), (D,L), (D,B), (F,R), (F,L), (B,L), (B,R)]

def face_to_cubie(s):
    f = [-1] * len(s)

    c = CubieCube.make_solved()

    for i in range(len(_CORNERS)):
        ud = 0
        for ud in range(_MAX_CO):
            tmp = f[_CORNLETS[i][ud]]
            if tmp == U or tmp == D:
                break
        col1 = f[_CORNLETS[i][(ud+1) % _MAX_CO]]
        col2 = f[_CORNLETS[i][(ud+2) % _MAX_CO]]
        for j in range(len(_CORNERS)):
            if _CORNERS[j][1] == col1 and _CORNERS[j][2] == col2:
                c.cp[i] = j
                c.co[i] = ud
                break


