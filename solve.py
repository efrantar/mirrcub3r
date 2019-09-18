from subprocess import Popen, PIPE
import time

N_THREADS = 12 # number of threads to use for solving
SOLVE_TIME = 25 # solving time in milliseconds
SCRAMBLE_TIME = 50 # scrambling time may be higher

# This is the move-order used by the solver
NAME_TO_MOVE = {m: i for i, m in enumerate([
    "U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", 
    "D", "D2", "D'", "L", "L2", "L'"
])}

# Transforms a solution string returned from the solver into a sequence of moves to be executed 
# by the robot. This includes conversion of move names into IDs and merging of consecutive
# quarter-turns (also axial ones) into half-turns.
def convert_sol(sol):
    if sol == '': # catch easy case to avoid any trouble below
        return []
    splits = sol.replace('(', '').replace(')', '').split(' ')
    axial = [('(' in m) for m in sol.split(' ')] # where axial moves start

    print(sol)

    # Perform the merging; note that we will never have to match a simple quarter turn
    # with a consecutive axial turn or a simple quarter turn with a non-adjacent simple 
    # quarter-turn as such solutions are never returned by the solver
    splits1 = []
    i = 0
    while i < len(splits):
        if axial[i]:
            if i < len(splits) - 2:
                if axial[i + 2]: # `splits[i + 3]` must exist
                    if splits[i] == splits[i + 2] and splits[i + 1] == splits[i + 3]:
                        splits1.append('%s2' % splits[i][:1])
                        splits1.append('%s2' % splits[i + 1][:1])
                        i += 4
                    else:
                        splits1 += splits[i:(i + 2)]
                        i += 2
                else:
                    if splits[i] == splits[i + 2]:
                        splits1.append('%s2' % splits[i][:1])
                        splits1.append(splits[i + 1])
                        i += 3
                    elif i < len(splits) - 3 and splits[i + 1] == splits[i + 2]:
                        splits1.append(splits[i])
                        splits1.append('%s2' % splits[i + 1][:1])
                        i += 3
                    else:
                        splits1 += splits[i:(i + 2)]
                        i += 2
            else:
                splits1 += splits[i:(i+2)]
                i += 2
        else:
            if i < len(splits) - 1:
                if axial[i + 1]: # `splits[i + 2]` must exist
                    # We will never have to merge both moves before and after into an axial one
                    if splits[i] == splits[i + 1]:
                        splits1.append('%s2' % splits[i + 1][:1])
                        splits1.append(splits[i + 2])
                        i += 3
                    elif splits[i] == splits[i + 2]:
                        splits1.append(splits[i + 1])
                        splits1.append('%s2' % splits[i + 2][:1])
                        i += 3
                    else:
                        splits1.append(splits[i])
                        i += 1
                else:
                    if splits[i] == splits[i + 1]:
                        splits1.append(splits[i][:1] + '2')
                        i += 2
                    else:
                        splits1.append(splits[i])
                        i += 1
            else:
                splits1.append(splits[i])
                i += 1

    print(splits1)

    return [NAME_TO_MOVE[m] for m in splits1] # finally convert names to move IDs

# Simple Python interface to the interactive mode of the "twophase" solver
class Solver:

    def __enter__(self):
        self.proc = Popen(
            ['./twophase', '-t', str(N_THREADS), 'interactive'], stdin=PIPE, stdout=PIPE
        )
        while 'Ready!' not in self.proc.stdout.readline().decode():
            pass # wait for everything to boot up
        return self # `__enter__` must retrun reference to initialized object

    def __exit__(self, exception_type, exception_value, traceback):
        self.proc.terminate()

    def solve(self, facecube):
        self.proc.stdin.write(('solve %s -1 %d\n' % (facecube, SOLVE_TIME)).encode())
        self.proc.stdin.flush() # command needs to be received instantly
        sol = self.proc.stdout.readline().decode()[:-1] # strip trailing '\n'
        self.proc.stdout.readline() # clear time taken message
        self.proc.stdout.readline() # clear "Ready!" message 
        return convert_sol(sol) if 'Error' not in sol else None

    def scramble(self):
        self.proc.stdin.write(('scramble %d\n' % SCRAMBLE_TIME).encode())
        self.proc.stdin.flush()
        scramble = self.proc.stdout.readline().decode()[:-1]
        self.proc.stdout.readline() # clear "Ready!" message
        return convert_sol(scramble) # scrambling will never fail

if __name__ == '__main__':
    with Solver() as solver:
        print(solver.scramble())

