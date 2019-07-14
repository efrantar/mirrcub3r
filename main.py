import subprocess
import numpy as np

GRID = [
    [200, 500], [525, 500], [835, 500], # 0, 1, 2
    [200, 815], [525, 815], [835, 815], # 0, 1, 3
    [200, 1130], [525, 1130], [835, 1130] # 0, 1, 4
]

SCAN_PROCESS = [
    (GRID[0], 0), # U1
    (GRID[1], 0), # U2
    (GRID[2], 0), # U3
    (GRID[3], 0), # U4
    (GRID[4], -1), # U5
    (GRID[5], 0), # U6
    (GRID[6], 0), # U7
    (GRID[7], 0), # U8
    (GRID[8], 0), # U9
    (GRID[6], 1), # R1
    (GRID[7], 9), # R2
    (GRID[0], 1), # R3
    (GRID[7], 1), # R4
    (GRID[4], -1), # R5
    (GRID[1], 1), # R6
    (GRID[8], 1), # R7
    (GRID[1], 9), # R8
    (GRID[2], 1), # R9
    (GRID[0], 4), # F1
    (GRID[5], 7), # F2
    (GRID[2], 4), # F3
    (GRID[3], 4), # F4
    (GRID[4], -1), # F5
    (GRID[5], 4), # F6
    (GRID[6], 4), # F7
    (GRID[3], 7), # F8
    (GRID[8], 4), # F9
    (GRID[8], 2), # D1
    (GRID[7], 2), # D2
    (GRID[6], 2), # D3
    (GRID[3], 5), # D4
    (GRID[4], -1), # D5
    (GRID[5], 5), # D6
    (GRID[2], 2), # D7
    (GRID[1], 2), # D8
    (GRID[0], 2), # D9
    (GRID[2], 3), # L1
    (GRID[7], 10), # L2
    (GRID[8], 3), # L3
    (GRID[1], 3), # L4
    (GRID[4], -1), # L5
    (GRID[7], 3), # L6
    (GRID[0], 3), # L7
    (GRID[1], 10), # L8
    (GRID[6], 3), # L9
    (GRID[8], 6), # B1
    (GRID[3], 8), # B2
    (GRID[6], 6), # B3
    (GRID[5], 6), # B4
    (GRID[4], -1), # B5
    (GRID[3], 6), # B6
    (GRID[2], 6), # B7
    (GRID[5], 8), # B8
    (GRID[0], 6)
]

CAM_URL = 'http://192.168.178.25:8080/shot.jpg'
SCAN_POSITIONS, SCAN_SCHEDULE = unzip(*SCAN_PROCESS)
SCAN_POSITIONS = np.array(SCAN_POSITIONS)
SCAN_SCHEDULE = np.array(SCAN_SCHEDULE)
SIZE2 = 75

SCAN_MOVES = [,
    ["F'", "B"],
    ["F'", "B"],
    ["F'", "B"],
    ["F'", "B", "L'", "R"],
    ["L'", "R"],
    ["L'", "R"],
    ["L'", "R", "F", "B'", "L'", "R"],
    ["L2", "R2"],
    ["L'", "R", "F'", "B", "L", "R'", "F'", "B"],
    ["F2", "B2"],
    ["F'", "B", "L'", "R"]
]

SCAN_ORDER = [4, 3, 0, 1, 5, 2]
# SCAN_TRANS = [5, 1, 0, 2, 3, 4]
# SCAN_COLOR = ['B', 'R', 'U', 'F', 'L', 'D']

NAME_TO_MOVE = {m: i for i, m in enumerate([
    "U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", 
    "D", "D2", "D'", "L", "L2", "L'"
])}

def solve(facecube):
    res = subprocess.check_output(['./twophase', 'twophase', facecube, '-1', '100']).decode().split('\n')
    return [NAME_TO_MOVE[m] for m in res[2].split(' ')] if not res[2].startswith('Error') else None

with Robot() as robot:
    cam = IpCam(CAM_URL)
    scanner = CubeScanner(cam, SCAN_SCHEDULE, SCAN_POSITIONS, SIZE2, per_col=8)

    for seq in SCAN_MOVES:
        scanner.next()
        for m in seq:
            robot.move(NAME_TO_MOVE[m])
    colors = scanner.finish())
    for f in range(6):
        colors[9 * f + 4] = SCAN_ORDER[f]

    facecube = ' ' * 54
    for f, f1 in enumerate(SCAN_TRANS):
        for i in range(9):
            facecube[9 * f1 + i


    sol = solve(facecube)
    if sol is not None:
        for m in sol:
            robot.move(m)
    else:
        print('Error ...')

