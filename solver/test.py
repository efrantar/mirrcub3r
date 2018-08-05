from cubie import *
from coord import *
from coord import _N_COORDS, MAX_MOVE_COUNT, _N_FRBR_2, _PHASE_2_PRUN_MOVES

_N_COORD_TYPES = 7

c = CubieCube.make_solved()
for coord in range(_N_COORD_TYPES):
    for i in range(_N_COORDS[coord]):
        c.set_coord(coord, i)
        if c.get_coord(coord) != i:
            print('Error')
print('OK')

for coord in range(_N_COORD_TYPES - 1): # URDF only valid for phase 2 moves thus omitted for now
    for i in range(_N_COORDS[coord]):
        for m in range(MAX_MOVE_COUNT * N_COLORS):
            i1 = i
            for _ in range(4):
                i1 = MOVE[coord][i1][m]
            if i1 != i:
                print('Error')
print('OK')

for i in range(_N_FRBR_2):
    for m in _PHASE_2_PRUN_MOVES:
        if MOVE[FRBR][i][m] >= 24:
            print('Error')
print('OK')
