def cmd_rot(ports, deg):
    return b''.join([
        ev3.opOutput_Step_Power,
        ev3.LCX(0),
        ev3.LCX(ports),
        ev3.LCX(100 if deg > 0 else -100),
        ev3.LCX(0),
        ev3.LCX(abs(deg)),
        ev3.LCX(0),
        ev3.LCX(1)
    ])

def cmd_readtacho(port):
    return = b''.join([
        ev3.opInput_Device,
        ev3.GET_RAW,
        ev3.LCX(0),
        ev3.port_motor_input(port),
        ev3.GVX(0)
    ])

def cmd_waitdeg(port, lv_start, lv_loop, deg):
    cmd = b''.join([
        ev3.opInput_Device,
        ev3.GET_RAW,
        ev3.LCX(0),
        ev3.port_motor_input(port),
        ev3.LVX(lv_loop),
        ev3.opSub32,
        ev3.LVX(lv_loop),
        ev3.LVX(lv_start),
        ev3.LVX(lv_loop)
    ]) # 9 bytes
    print(len(cmd))
    return []
    if deg > 0:
        cmd += b''.join([
            ev3.opJr_Lt32,
            ev3.LVX(lv_loop),
            ev3.LCX(deg),
            ev3.LCX(-9)
        ])
    else:
        cmd += b''.join([
            ev3.opJr_Gt32,
            ev3.LVX(lv_loop),
            ev3.LCX(deg),
            ev3.LCX(-9)
        ])
    return cmd

def cmd_rotretearly(ports, deg, port, early, ports1=0, deg1=0, after=0):
    cmd = b''.join([
        ev3.opInput_Device,
        ev3.GET_RAW,
        ev3.LCX(0),
        ev3.port_motor_input(port),
        ev3.LVX(0)
    ])
    cmd += cmd_rot(ports, deg)
    if ports1 > 0:
        cmd += cmd_rot(ports1, deg1)
    if after > 0:
        cmd += cmd_waitdeg(port, 0, 4, after if deg > 0 else -after)
    cmd += cmd_waitdeg(port, 0, 4, deg - early if deg > 0 else deg + early) 
    return cmd

ROTRETEARLY_MEM = 8

import ev3
import time

brick = ev3.EV3(protocol='Usb', host='00:16:53:40:CE:B6')



cmd = cmd_rotretearly(ev3.PORT_A, 90, ev3.PORT_A, 5)
tick = time.time()
brick.send_direct_cmd(cmd, local_mem=ROTRETEARLY_MEM)
print(time.time() - tick)

