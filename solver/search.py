from coord import *
from coord import _N_COORDS, _PHASE2_MOVES


_PHASE1_COORDS = [TWIST, FLIP, FRBR]
_PHASE2_COORDS = [FRBR, URFDLF, URDF, PAR]
# The transistion to phase 2 happens in two steps as cancelling after step 1 saves quite a bit of time.
_PHASE12_COORDS1 = [URFDLF, PAR]
_PHASE12_COORDS2 = [URUL, UBDF]

_PHASE2_DMAX_MIN = 5 # maximum phase 1 depth for which we do phase 2 iterative deepening
_PHASE2_DMAX = 10 # maximum allowed phase 2 depth; suggested by Kociemba

_DMAX = 50 # just needs to be larger than any reasonable number of moves
_coords = [[-1] * len(_N_COORDS) for _ in range(_DMAX)]
_moves = [-MOVES_PER_FACE] * _DMAX # make sure that the last entry // MAX_MOVE_COUNT is always -1

def phase1(d, dmax):
    prun = max(
        get_prun(FRBR_TWIST_PRUN, phase1_prun_idx(_coords[d][TWIST], _coords[d][FRBR])),
        get_prun(FRBR_FLIP_PRUN, phase1_prun_idx(_coords[d][FLIP], _coords[d][FRBR]))
    )

    if prun > dmax - d:
        return -1
    if prun == 0:
        if dmax > _PHASE2_DMAX_MIN:
            dmax = min(d + _PHASE2_DMAX, _DMAX)

        for i in range(d):
            _move(i, _moves[i], _PHASE12_COORDS1)

        if get_prun(
            FRBR_URFDLF_PAR_PRUN, phase2_prun_idx(_coords[d][URFDLF], _coords[d][FRBR], _coords[d][PAR])
        ) > dmax - d:
            return -1

        for i in range(d):
            _move(i, _moves[i], _PHASE12_COORDS2)
        _coords[d][URDF] = URDF_MERG[_coords[d][URUL]][_coords[d][UBDF]]

        if dmax <= _PHASE2_DMAX_MIN:
            # In this case we also do iterative deepening on phase 2. This is to make the solver find short solutions
            # for easy cubes.
            for i in range(d, dmax + 1):
                tmp = phase2(d, dmax + 1)
                if tmp != -1:
                    return tmp
            return -1
        return phase2(d, dmax)

    for m in range(N_MOVES):
        if m // MOVES_PER_FACE != _moves[d - 1] // MOVES_PER_FACE:
            _move(d, m, _PHASE1_COORDS)
            tmp = phase1(d + 1, dmax)
            if tmp != -1:
                return tmp
    return -1

def phase2(d, dmax):
    prun = max(
        get_prun(FRBR_URFDLF_PAR_PRUN, phase2_prun_idx(_coords[d][URFDLF], _coords[d][FRBR], _coords[d][PAR])),
        get_prun(FRBR_URDF_PAR_PRUN, phase2_prun_idx(_coords[d][URDF], _coords[d][FRBR], _coords[d][PAR]))
    )
    if prun > dmax - d:
        return -1
    if prun == 0:
        return d

    for m in _PHASE2_MOVES:
        if m // MOVES_PER_FACE != _moves[d - 1] // MOVES_PER_FACE:
            _move(d, m, _PHASE2_COORDS)
            tmp = phase2(d + 1, dmax)
            if tmp != -1:
                return tmp
    return -1

def _move(d, m, cs):
    for c in cs:
        _coords[d+1][c] = MOVE[c][_coords[d][c]][m]
    _moves[d] = m


_MOVE_STR = [c + cnt for c in COL for cnt in ['', '2', "'"]]

def search(s, max):
    c = face_to_cubie(s)
    if c is None or not c.check():
        return None

    # The `URDF` is reconstructed by merging upon entering phase 2 and is not relevant beforehand.
    _coords[0] = [c.get_coord(i) if i != URDF else -1 for i in range(len(_N_COORDS))]

    global _DMAX # to avoid an additional recursion parameters
    _DMAX = max
    for i in range(max + 1):
        sol = phase1(0, i)
        if sol != -1:
            return ' '.join(map(lambda m: _MOVE_STR[m], _moves[:sol]))
