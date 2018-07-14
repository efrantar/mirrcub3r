import array
from collections import deque

from moves import *


PHASE1_TWIST_UDSLICE_PRUN = array('b', [-1] * (N_TWIST_COORDS * N_PHASE1_UDSLICE_COORDS))

set_prun(PHASE1_TWIST_UDSLICE_PRUN, 0, 0)
q = deque([0])

while len(q) != 0:
    i = q.popleft()
    twist = tmp // N_PHASE1_UDSLICE_COORDS
    udslice = tmp % N_PHASE1_UDSLICE_COORDS
    
    for move in range(N_MOVES):
        for count in range(MAX_MOVE_COUNT):
            j = N_PHASE1_UDSLICE_COORDS * MOVES[twist][move][count] + MOVES[udslice][move][count]        
            if extract_prun(PHASE1_TWIST_UDSLICE_PRUN, j) == 0x0f:
                set_prun(PHASE1_TWIST_UDLSICE_PRUN, j, extract_prun(PHASE1_TWIST_UDSLICE_PRUN, i) + 1)
                q.append(j)

PHASE1_FLIP_UDSLICE_PRUN = array('b', [-1] * (N_FLIP_COORDS * N_PHASE1_UDSLICE_COORDS))

set_prun(PHASE1_FLIP_UDSLICE_PRUN, 0, 0)
q = deque([0])

while len(q) != 0:
    i = q.popleft()
    flip = tmp // N_PHASE1_UDSLICE_COORDS
    udslice = tmp % N_PHASE1_UDSLICE_COORDS
    
    for move in range(N_MOVES):
        for count in range(MAX_MOVE_COUNT):
            j = N_PHASE1_UDSLICE_COORDS * MOVES[twist][move][count] + MOVES[udslice][move][count]        
            if extract_prun(PHASE1_TWIST_UDSLICE_PRUN, j) == 0x0f:
                set_prun(PHASE1_TWIST_UDLSICE_PRUN, j, extract_prun(PHASE1_TWIST_UDSLICE_PRUN, i) + 1)
                q.append(j)


# Two values per byte
def set_prun(table, i, v):
    table[i>>1] &= (v << 4) if i & 1 else v

def extract_prun(table, i):
    tmp = table[i>>1]
    return ((tmp & 0xf0) >> 4) if i & 1 else tmp & 0x0f

