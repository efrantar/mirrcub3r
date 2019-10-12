# Script used for testing the robot's moveset.

from control import *
import time

MOVES = [
    "U", "U2", "U'", "R", "R2", "R'", 
    "F", "F2", "F'", "D", "D2", "D'", 
    "L", "L2", "L'", "B", "B2", "B'"
]

def moves(s):
    return [MOVES.index(s) for s in s.split(' ')]

SEQ1 = [3, 14, 1, 10, 12, 1, 13, 6, 2, 11, 3, 8, 0, 11, 5, 12, 9, 8, 0, 5, 14, 6, 5, 14, 6, 5]
SEQ2 = [0, 9, 6, 11, 5, 2, 3, 2, 11, 5, 14, 6, 5, 14, 6, 2, 14, 7, 4, 7, 0, 11, 4]
SEQ3 = [3, 12, 1, 5, 13, 1, 10, 5, 6, 0, 11, 14, 9, 12, 11, 13, 0, 3, 2, 11, 3, 12, 8]

robot = Robot()
print('Connected.')

tick = time.time()

# robot.execute([9, 3, 2, 5, 12, 0, 11, 8, 5, 14, 6, 5, 14, 2, 8, 3, 12, 0, 9, 5, 14, 11, 4, 0, 10, 4, 2, 11])
# robot.execute([0, 9, 4, 2, 10, 4, 9, 3, 12, 2, 11, 5, 14, 6, 0, 3, 12, 8, 3, 12, 6, 2, 9, 3, 14, 0, 5, 11])
# robot.execute(moves("U2 F2 R2 D' U L2 D' U2 F' U L2 U' F2 R2 D' L U' F' R F' U'"))

# robot.execute([6, 3, 14, 2, 11, 3, 12, 2, 6, 0, 9, 5, 6, 0, 9, 5, 14, 0, 11, 8, 5, 1, 10, 5, 12, 1, 10, 3, 7])
robot.execute([7, 5, 1, 10, 3, 14, 1, 10, 3, 6, 2, 9, 3, 12, 2, 11, 8, 3, 2, 11, 8, 0, 5, 14, 0, 9, 5, 12, 8])
#robot.execute([3, 8, 3, 12, 8, 3, 12, 2, 6, 11, 3, 14, 2, 9, 6, 5, 0, 9, 8, 13, 1, 14, 1, 10, 5, 12])

# robot.execute(moves("D L U R F D L U R F U D R' L' U D R' L' U D R' L' U D R' L' U D R' L'"))
# robot.execute(moves("D' L' U' R' F' D' L' U' R' F' U' D' R L U' D' R L U' D' R L U' D' R L U' D' R L"))

# robot.execute(moves("D L' U R' F D' L U' R F' D L' U R' F D' L U' R F'"))
# robot.execute(moves("D L U R F D L U R F D L U R F D L U R F"))
# robot.execute(moves("D L' U R F' D' L U' R F D' L U' R' F D L' U R' F'"))

# robot.execute(moves("D' R L U' R L F' R L D' R L U'"))
# robot.execute(moves("U D R' U D L'"))

# robot.execute(moves("D R' L U R' L F R L' D R L' U R' L F R L'"))
# robot.execute(moves("R D U' L D' U R D U' L D' U"))

# robot.execute(moves("D R L U R L F R L D R L U R L F R L"))
# robot.execute(moves("L U D R U D F U D L"))

# robot.execute(moves("U D R' L' U D R' L' U D R' L'"))
# robot.execute(moves("U D R' L U D' R L' U D R' L"))
# robot.execute(moves("U D R L U D R L U D R L"))

# robot.execute(moves("D2 L2 U2 R2 F2 D2 L2 U2 R2 F2"))
# robot.execute(moves("U2 D2 R2 L2 U2 D2 R2 L2"))
# robot.execute(moves("U D2 R2 L U2 D R L2"))
# robot.execute(moves("U2 D L D U2 F' R2 L U"))

print(time.time() - tick)

