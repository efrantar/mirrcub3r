from face import *
from cubie import *

from array import * # arrays are much space efficient for storing primitive datatypes
from collections import deque
import os
import pickle


MOVES_PER_FACE = 3
N_MOVES = N_COLORS * MOVES_PER_FACE

def _move_idx(face, cnt):
    return MOVES_PER_FACE * face + cnt

def _gen_movetable(n, coord, mul):
    # Note that we need to create a new object for every entry and hence can't just multiply the list by n.
    moves = [array('i', [-1] * N_MOVES) for _ in range(n)]

    c = CubieCube.make_solved()
    for i in range(n):
        c.set_coord(coord, i)
        for face in range(N_COLORS):
            for cnt in range(MOVES_PER_FACE):
                c.mul(mul, MOVES[face])
                moves[i][_move_idx(face, cnt)] = c.get_coord(coord)
            c.mul(mul, MOVES[face]) # restore original state

    return moves

_N_COORDS = [
    (MAX_CO + 1) ** (N_CORNERS-1), # TWIST
    (MAX_EO + 1) ** (N_EDGES-1), # FLIP
    FAC[len(FRBR_EDGES)] * CNK[N_EDGES][len(FRBR_EDGES)], # FRBR
    FAC[len(URFDLF_CORNERS)] * CNK[N_CORNERS][len(URFDLF_CORNERS)], # URFDLF
    FAC[len(URUL_EDGES)] * CNK[N_EDGES][len(URUL_EDGES)], # URUL
    FAC[len(UBDF_EDGES)] * CNK[N_EDGES][len(UBDF_EDGES)], # UBDF
    FAC[len(URDF_EDGES)] * CNK[N_EDGES - len(FRBR_EDGES)][len(URDF_EDGES)], # URDF
    2 # PAR
]
_MUL = [CORNERS, EDGES, EDGES, CORNERS, EDGES, EDGES, EDGES] # TWIST, FLIP, FRBR, URFDLF, URUL, UBDF, URDF


# Assumes all bits are set to 1.
def _set_prun(table, i, v):
    table[i>>1] &= (v << 4) | 0xf if i & 1 else 0xf0 | v

def get_prun(table, i):
    tmp = table[i>>1]
    return ((tmp & 0xf0) >> 4) if i & 1 else tmp & 0x0f

_N_FRBR_1 = CNK[N_EDGES][len(FRBR_EDGES)] # the permutation part is irrelevant in phase 1
_N_FRBR_2 = FAC[len(FRBR_EDGES)] # in phase 2 the orientation part is always 0

def phase1_prun_idx(c, frbr):
    return _N_FRBR_1 * c + frbr // _N_FRBR_2 # we need to divide out the irrelevant permutation component

def _gen_phase1_pruntable(n, coord):
    # Make all bits on per default, which allows detecting empty cells as 0xf (possible as all values will be < 15).
    prun = array('B', [0xff] * n)

    _set_prun(prun, 0, 0)
    q = deque([0])

    while len(q) != 0:
        i = q.popleft()
        c = i // _N_FRBR_1
        frbr = i % _N_FRBR_1

        for m in range(MOVES_PER_FACE * N_COLORS):
            # The FRBR move-table assumes that the permutation part is present, so we simply set it to 0.
            j = phase1_prun_idx(MOVE[coord][c][m], MOVE[FRBR][frbr * _N_FRBR_2][m])
            if get_prun(prun, j) == 0xf:
                _set_prun(prun, j, get_prun(prun, i) + 1)
                q.append(j)

    return prun

_N_PER_BYTE = 2

_PHASE2_MOVES = [
    _move_idx(f, c) for f, c in [(U,0), (U,1), (U,2), (R,1), (F,1), (D,0), (D,1), (D,2), (L,1), (B,1)]
] # U, U2, U', R2, F2, D, D2, D', L2, B2

def phase2_prun_idx(c, frbr, par):
    return (_N_FRBR_2 * c + frbr) * _N_COORDS[PAR] + par

def _gen_phase2_pruntable(coord):
    prun = array('B', [255] * (_N_FRBR_2 * _N_COORDS[coord] * _N_COORDS[PAR] / _N_PER_BYTE))

    _set_prun(prun, 0, 0)
    q = deque([0])

    while len(q) != 0:
        i = q.popleft()
        par = i % _N_COORDS[PAR]
        c = (i // _N_COORDS[PAR]) // _N_FRBR_2
        frbr = (i // _N_COORDS[PAR]) % _N_FRBR_2

        for m in _PHASE2_MOVES:
            j = phase2_prun_idx(MOVE[coord][c][m], MOVE[FRBR][frbr][m], MOVE[PAR][par][m])
            if get_prun(prun, j) == 0xf:
                _set_prun(prun, j, get_prun(prun, i) + 1)
                q.append(j)

    return prun

_N_URUL_UBDF_2 = FAC[len(URUL_EDGES)] * CNK[N_EDGES - len(FRBR_EDGES)][len(URUL_EDGES)]


_FILE = '../res/tables'

if os.path.exists(_FILE):
    MOVE, FRBR_TWIST_PRUN, FRBR_FLIP_PRUN, FRBR_URFDLF_PAR_PRUN, FRBR_URDF_PAR_PRUN, URDF_MERG = \
        pickle.load(open(_FILE, 'rb'))
else:
    # TWIST, FLIP, FRBR, URFDLF, URUL, UBDF, URDF
    MOVE = [_gen_movetable(_N_COORDS[i], i, _MUL[i]) for i in range(len(_N_COORDS) - 1)] # skip PAR

    # Hardcoding this here avoids having to reconstruct the PAR coordinate
    MOVE.append([
        array('i', [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1]),
        array('i', [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
    ])  # ..., PAR

    # Number of entries is not even, hence we have to allocate one more cell.
    FRBR_TWIST_PRUN = _gen_phase1_pruntable(_N_COORDS[TWIST] * _N_FRBR_1 / _N_PER_BYTE + 1, TWIST)
    FRBR_FLIP_PRUN = _gen_phase1_pruntable(_N_COORDS[FLIP] * _N_FRBR_1 / _N_PER_BYTE, FLIP)

    FRBR_URFDLF_PAR_PRUN = _gen_phase2_pruntable(URFDLF)
    FRBR_URDF_PAR_PRUN = _gen_phase2_pruntable(URDF)

    URDF_MERG = [array('i', [merge_urdf(i, j) for j in range(_N_URUL_UBDF_2)]) for i in range(_N_URUL_UBDF_2)]

    pickle.dump(
        (MOVE, FRBR_TWIST_PRUN, FRBR_FLIP_PRUN, FRBR_URFDLF_PAR_PRUN, FRBR_URDF_PAR_PRUN, URDF_MERG),
        open(_FILE, 'wb')
    )
