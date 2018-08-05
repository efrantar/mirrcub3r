from face import *
from cubie import *

from array import *
from collections import deque
import os
import pickle


MAX_MOVE_COUNT = 3

def _gen_movetable(n, coord, mul):
    moves = [array('i', [-1] * MAX_MOVE_COUNT * N_COLORS) for _ in range(n)]

    c = CubieCube.make_solved()
    for i in range(n):
        c.set_coord(coord, i)
        for face in range(N_COLORS):
            for cnt in range(MAX_MOVE_COUNT):
                c.mul(mul, MOVES[face])
                moves[i][MAX_MOVE_COUNT * face + cnt] = c.get_coord(coord)
            c.mul(mul, MOVES[face]) # restore original state

    return moves

_N_COORDS = [
    2187, # 3^7; TWIST
    2048, # 2^11; FLIP
    11880, # 12!/(12-4)!; FRBR
    20160, # 8!/(8-6)!; URFDLF
    1320, # 12!/(12-3)!; URUL
    1320, # 12!/(12-3)!; UBDF
    20160, # 8!/(8-6)!; URDF
    2 # 2; PAR
]
_MUL = [CORNERS, EDGES, EDGES, CORNERS, EDGES, EDGES, EDGES] # TWIST, FLIP, FRBR, URFDLF, URUL, UBDF, URDF

N_MOVES = N_COLORS * MAX_MOVE_COUNT


def _set_prun(table, i, v):
    table[i>>1] &= (v << 4) if i & 1 else v

def get_prun(table, i):
    tmp = table[i>>1]
    return ((tmp & 0xf0) >> 4) if i & 1 else tmp & 0x0f

_N_FRBR_1 = 495 # 12 choose 4
_N_FRBR_2 = 24 # 4!

def phase1_prun_idx(c, frbr):
    return _N_FRBR_1 * c + frbr / _N_FRBR_2

def _gen_phase1_pruntable(n, coord):
    # Make all bits on per default -> detect empty cells as 0xf
    prun = array('B', [255] * n)

    _set_prun(prun, 0, 0)
    q = deque([0])

    while len(q) != 0:
        i = q.popleft()
        c = i // _N_FRBR_1
        frbr = i % _N_FRBR_1

        for m in range(MAX_MOVE_COUNT * N_COLORS):
            # Permutation irrelevant for phase 1
            j = phase1_prun_idx(MOVE[coord][c][m], MOVE[FRBR][frbr * _N_FRBR_2][m])
            if get_prun(prun, j) == 0x0f:
                _set_prun(prun, j, get_prun(prun, i) + 1)
                q.append(j)

    return prun

_N_PER_BYTE = 2

_PHASE_2_PRUN_MOVES = [0, 1, 2, 4, 7, 9, 10, 11, 13, 16] # U, U2, U', R2, F2, D, D2, D', L2, B2

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

        for m in _PHASE_2_PRUN_MOVES:
            j = phase2_prun_idx(MOVE[coord][c][m], MOVE[FRBR][frbr][m], MOVE[PAR][par][m])
            if get_prun(prun, j) == 0x0f:
                _set_prun(prun, j, get_prun(prun, i) + 1)
                q.append(j)

    return prun

_N_URUL_UBDF_2 = 336 # 8!/(8-3)!


_FILE = '../res/tables'

if os.path.exists(_FILE):
    MOVE, FRBR_TWIST_PRUN, FRBR_FLIP_PRUN, FRBR_URFDLF_PAR_PRUN, FRBR_URDF_PAR_PRUN, URDF_MERG = \
        pickle.load(open(_FILE, 'rb'))
else:
    # TWIST, FLIP, FRBR, URFDLF, URUL, UBDF, URDF
    MOVE = [_gen_movetable(_N_COORDS[i], i, _MUL[i]) for i in range(len(_N_COORDS) - 1)] # skip PAR

    MOVE.append([
        array('i', [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1]),
        array('i', [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0])
    ])  # ..., PAR

    FRBR_TWIST_PRUN = _gen_phase1_pruntable(_N_COORDS[TWIST] * _N_FRBR_1 / _N_PER_BYTE + 1, TWIST)
    FRBR_FLIP_PRUN = _gen_phase1_pruntable(_N_COORDS[FLIP] * _N_FRBR_1 / _N_PER_BYTE, FLIP)

    FRBR_URFDLF_PAR_PRUN = _gen_phase2_pruntable(URFDLF)
    FRBR_URDF_PAR_PRUN = _gen_phase2_pruntable(URDF)

    URDF_MERG = [array('i', [merge_urdf(i, j) for j in range(_N_URUL_UBDF_2)]) for i in range(_N_URUL_UBDF_2)]

    pickle.dump(
        (MOVE, FRBR_TWIST_PRUN, FRBR_FLIP_PRUN, FRBR_URFDLF_PAR_PRUN, FRBR_URDF_PAR_PRUN, URDF_MERG),
        open(_FILE, 'wb')
    )

print('Tables loaded.')
