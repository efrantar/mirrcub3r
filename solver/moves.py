from cubie import *


c = CubieCube.make_solved()

# Memory consumption negligible in comparison to pruning tables
TWIST_MOVE = [[[0] * MAX_MOVE_COUNT] * N_MOVES] * N_TWIST_COORDS

for i in range(N_TWIST_COORDS):
    c.decode_twist_coord(i)
    for move in range(N_MOVES):
        for count in range(MAX_MOVE_COUNT):
            c.mul_corners(CubieCube.MOVES[move])
            TWIST_MOVE[i][move][count] = c.twist_coord()
        c.mul_corners(CubieCube.MOVES[move]) # restore original state

FLIP_MOVE = [[[0] * MAX_MOVE_COUNT] * N_MOVES] * N_FLIP_COORDS

for i in range(N_FLIP_COORDS):
    c.decode_flip_coord(i)
    for move in range(N_MOVES):
        for count in range(MAX_MOVE_COUNT):
            c.mul_edges(CubieCube.MOVES[move])
            FLIP_MOVE[i][move][count] = c.flip_coord()
        c.mul_edges(CubieCube.MOVES[move])
        
PHASE1_UDSLICE_MOVE = [[[0] * MAX_MOVE_COUNT] * N_MOVES] * N_PHASE1_UDSLICE_COORDS

for i in range(N_PHASE1_UDSLICE_COORDS):
    c.decode_phase1_udslice_coord(i)
    for move in range(N_MOVES):
        for count in range(MAX_MOVE_COUNT):
            c.mul_edges(CubieCube.MOVES[move])
            FLIP_MOVE[i][move][count] = c.phase1_udslice_coord()
        c.mul_edges(CubieCube.MOVES[move])

