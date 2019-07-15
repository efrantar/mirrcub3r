import subprocess
import threading
import numpy as np

GRID = [
    [200, 500], [525, 500], [835, 500], # 0, 1, 2
    [200, 815], [525, 815], [835, 815], # 3, 4, 5
    [200, 1130], [525, 1130], [835, 1130] # 6, 7, 8
]

SCAN_PROCESS = [
    (GRID[0], 3), # U1
    (GRID[5], 9), # U2
    (GRID[2], 3), # U3
    (GRID[3], 3), # U4
    (GRID[4], -1), # U5
    (GRID[5], 3), # U6
    (GRID[6], 3), # U7
    (GRID[3], 9), # U8
    (GRID[8], 3), # U9
    (GRID[8], 4), # R1
    (GRID[1], 4), # R2
    (GRID[6], 4), # R3
    (GRID[7], 7), # R4
    (GRID[4], -1), # R5
    (GRID[1], 7), # R6
    (GRID[2], 4), # R7
    (GRID[7], 4), # R8
    (GRID[0], 4), # R9
    (GRID[0], 2), # F1
    (GRID[7], 5), # F2
    (GRID[2], 2), # F3
    (GRID[3], 2), # F4
    (GRID[4], -1), # F5
    (GRID[5], 2), # F6
    (GRID[6], 2), # F7
    (GRID[1], 5), # F8
    (GRID[8], 2), # F9
    (GRID[8], 1), # D1
    (GRID[5], 10), # D2
    (GRID[6], 1), # D3
    (GRID[5], 1), # D4
    (GRID[4], -1), # D5
    (GRID[3], 1), # D6
    (GRID[2], 1), # D7
    (GRID[3], 10), # D8
    (GRID[0], 1), # D9
    (GRID[8], 6), # L1
    (GRID[1], 6), # L2
    (GRID[6], 6), # L3
    (GRID[1], 8), # L4
    (GRID[4], -1), # L5
    (GRID[7], 8), # L6
    (GRID[2], 6), # L7
    (GRID[7], 6), # L8
    (GRID[0], 6), # L9
    (GRID[8], 0), # B1
    (GRID[7], 0), # B2
    (GRID[6], 0), # B3
    (GRID[5], 0), # B4
    (GRID[4], -1), # B5
    (GRID[3], 0), # B6
    (GRID[2], 0), # B7
    (GRID[1], 0), # B8
    (GRID[0], 0) # B9
]

CAM_URL = 'http://192.168.178.25:8080/shot.jpg'
SCAN_POSITIONS, SCAN_SCHEDULE = unzip(*SCAN_PROCESS)
SCAN_POSITIONS = np.array(SCAN_POSITIONS)
SCAN_SCHEDULE = np.array(SCAN_SCHEDULE)
SIZE2 = 75

SCAN_MOVES = [
    ["L", "R'"],
    ["L", "R'"],
    ["L", "R'"],
    ["L", "R'", "U'", "D"],
    ["L", "R'"],
    ["L", "R'"],
    ["L", "R'", "L'", "R", "U'", "D"],
    ["U2", "D2"],
    ["U'", "D", "L", "R'", "U", "D'", "L'", "R"]
    ["L2", "R2"],
    ["L", "R'", "U'", "D"]
]

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

    def run_parallel(m1, m2):
        thread1 = threading.Thread(lambda: robot.move(m1))
        thread2 = threading.Thread(lambda: robot.move(m2))
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

    for seq in SCAN_MOVES:
        scanner.next()
        for i in range(len(seq) - 1)
            run_parallel(NAME_TO_MOVE[seq[i]], NAME_TO_MOVE[seq[i + 1]])
    colors = scanner.finish()
    for f in range(6):
        colors[9 * f + 4] = SCAN_ORDER[f]
    facecube = [SCAN_COLOR[c] for c in colors]

    sol = solve(facecube)
    if sol is not None:
        for m in sol:
            robot.move(m)
        print('Done!')
    else:
        print('Error ...')

