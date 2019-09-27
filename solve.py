# This file handles computing actual solutions by interfacing with the C++ solver.

from subprocess import Popen, PIPE
import time

N_THREADS = 12
SOLVE_TIME = 25
SCRAMBLE_TIME = 50 # we don't care too much about speed when scrambling

# The robot's move order, actually different from the solver's
NAME_TO_MOVE = {m: i for i, m in enumerate([
    "U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", 
    "D", "D2", "D'", "L", "L2", "L'"
])}

# TODO: There is still some small ~1/100 "blemish" in the solver where we get solutions like 
# (U D) U' due to not applying any move restrictions in the phase 2 transistions. This causes 
# trouble for our robot but we will handle this on the solver level at a later time.
# TODO: Make the merging a solver feature in general (i.e. with a "-c" option).

# Convert string solution to move IDs and merge consecutive quarter-turns (also axial ones)  to half-turns
def convert_sol(sol):
    if sol == '':
        return []
    splits = sol.replace('(', '').replace(')', '').split(' ')
    axial = [('(' in m) for m in sol.split(' ')] # where axial moves start

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
                    elif splits[i + 1] == splits[i + 2]:
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

    return [NAME_TO_MOVE[m] for m in splits1] # finally convert names to move IDs

# Simple Python interface to the interactive mode of the "twophase" solver
class Solver:

    def __enter__(self):
        self.proc = Popen(
            ['./twophase', '-t', str(N_THREADS), 'interactive'], stdin=PIPE, stdout=PIPE
        )
        while 'Ready!' not in self.proc.stdout.readline().decode():
            pass # wait for everything to boot up
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.proc.terminate()

    def solve(self, facecube):
        self.proc.stdin.write(('solve %s -1 %d\n' % (facecube, SOLVE_TIME)).encode())
        self.proc.stdin.flush() # command needs to be received instantly
        sol = self.proc.stdout.readline().decode()[:-1] # strip trailing '\n'
        print(sol) # TODO: here for debugging purposes
        self.proc.stdout.readline() # clear time taken message
        self.proc.stdout.readline() # clear "Ready!" message 
        return convert_sol(sol) if 'Error' not in sol else None

    def scramble(self):
        self.proc.stdin.write(('scramble %d\n' % SCRAMBLE_TIME).encode())
        self.proc.stdin.flush()
        scramble = self.proc.stdout.readline().decode()[:-1]
        self.proc.stdout.readline() # "Ready!"
        print(scramble)
        return convert_sol(scramble) # scrambling will never fail

if __name__ == '__main__':
    with Solver() as solver:
        print(solver.scramble())

