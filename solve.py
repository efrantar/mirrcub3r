from subprocess import Popen, PIPE
import time

# This is the move-order used by the solver
NAME_TO_MOVE = {m: i for i, m in enumerate([
    "U", "U2", "U'", "R", "R2", "R'", "F", "F2", "F'", 
    "D", "D2", "D'", "L", "L2", "L'"
])}

class Solver:

    def __enter__(self):
        self.proc = Popen(
            ['./twophase', '-t', '12', 'interactive'], stdin=PIPE, stdout=PIPE
        )
        while 'Ready!' not in self.proc.stdout.readline().decode():
            pass # wait for everything to boot up
        return self # `__enter__` must retrun reference to initialized object

    def __exit__(self, exception_type, exception_value, traceback):
        self.proc.terminate()

    def solve(self, facecube):
        self.proc.stdin.write((facecube + ' -1 50\n').encode())
        self.proc.stdin.flush() # command needs to be received instantly
        sol = self.proc.stdout.readline().decode()[:-1] # strip trailing '\n'
        self.proc.stdout.readline() # time taken
        self.proc.stdout.readline() # "Ready!" message
        
        # Remove axial move-indicators (the solver does not need them at the moment)
        sol = sol.replace('(', '').replace(')', '')
        return [NAME_TO_MOVE[m] for m in sol.split(' ')] if sol != '' else [] # `''.split() == ['']`

