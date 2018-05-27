#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import random
import time

m1 = ev3.LargeMotor('outA')
m1.speed_sp = 200
m2 = ev3.MediumMotor('outC')
m2.speed_sp = 300

t = time.time()
for i in range(25):
	m = [m1, m2][random.randrange(2)]
	m.run_to_rel_pos(position_sp = [90, -90, 180][random.randrange(3)])
	m.wait_until_not_moving()

print(time.time() - t)

