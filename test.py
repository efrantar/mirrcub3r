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

# Scramble for the 0.929 solve
# robot.execute(moves("L2 U' F2 U' R' L U R' U' D' R L F' D R' U D L' U D' R U"))

# Sample scramble for POV solve video
# robot.execute(moves("D R2 L2 U D R2 L2 F R L D R L U D L' F D' R' D' L F D R' U'"))
# robot.execute(moves("U R D' F' L' D R D F' L U' D' R' L' D' R' L' F' R2 L2 U' D' R2 L2 D'"))

# Moveset demo
# robot.execute(moves(
#     "U R F' D L' R' U R' L F U D R' L' U' D F R L U D " +
#     "R2 F D2 L' U2 D2 F' R2 L2 U R2 L2 U' D' R2 L2 U D"
# ))

# Try some solves
# robot.execute(SEQ1)

# Quarter-turn corner cutting tests
# robot.execute(moves("U R' F D' L U' R F' D L' U R' F D' L U' R F' D L'"))
# robot.execute(moves("U R F D L U R F D L U R F D L U R F D L"))
# robot.execute(moves("U D R' U D L' U D R' U D L' U D"))
# robot.execute(moves("U D' R U' D L U D' R U' D L U D'"))
# robot.execute(moves("U D R U D L U D R U D L U D R"))
# robot.execute(moves("U D R' L' U D R' L' U D R' L' U D R' L' U D R' L'"))
# robot.execute(moves("U D R' L U D R L' U D R' L U D R L'"))
# robot.execute(moves("U D R L U D R L U D R L U D R L U D R L"))

# Half-turn corner cutting tests

# robot.execute(moves("U' R2 F' D2 L' U2 R' F2 D' L2 U' R2 F' D2 L' U2 R' F2 D' L2"))
# robot.execute(moves("U R2 F D2 L U2 R F2 D L2 U R2 F D2 L U2 R F2 D L2"))

# robot.execute(moves("U2 D2 R' U2 D2 L' U2 D2 R' U2 D2 L' U2 D2"))
# robot.execute(moves("U' D' R2 U' D' L2 U' D' R2 U' D' L2 U' D'"))

# robot.execute(moves("U D' R2 U' D L2 U D' R2 U' D L2 U D'"))

# robot.execute(moves("U2 D2 R U2 D2 L U2 D2 R U2 D2 L U2 D2"))
# robot.execute(moves("U D R2 U D L2 U D R2 U D L2 U D"))

# robot.execute(moves("U2 D2 R' L' U2 D2 R' L' U2 D2 R' L'"))
# robot.execute(moves("U2 D2 R L' U2 D2 R' L U2 D2 R L'"))
# robot.execute(moves("U2 D2 R2 L2 U2 D2 R2 L2 U2 D2 R2 L2"))

print(time.time() - tick)

