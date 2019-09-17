import struct
import time

import ev3

def test(brick, ports, port1, deg, deg1):
    cmd = b''.join([
        ev3.opInput_Device,
        ev3.GET_RAW,
        ev3.LCX(0),
        ev3.port_motor_input(port1),
        ev3.GVX(0),
        ev3.opOutput_Step_Power,
        ev3.LCX(0),
        ev3.LCX(ports),
        ev3.LCX(100),
        ev3.LCX(0),
        ev3.LCX(deg),
        ev3.LCX(0),
        ev3.LCX(1),
        ev3.opAdd32,
        ev3.GVX(0),
        ev3.LCX(deg1),
        ev3.GVX(0),
        ev3.opInput_Device,
        ev3.GET_RAW,
        ev3.LCX(0),
        ev3.port_motor_input(port1),
        ev3.GVX(4),
        ev3.opJr_Lt32,
        ev3.GVX(4),
        ev3.GVX(0),
        ev3.LCX(-9)
    ])
    ret = brick.send_direct_cmd(cmd, global_mem=8)
    return struct.unpack('<ii', ret[5:])

def is_pressed(brick, port):
    cmd = b''.join([
        ev3.opInput_Read,
        ev3.LCX(0),
        ev3.LCX(port),
        ev3.LCX(16),
        ev3.LCX(0),
        ev3.GVX(0)
    ])
    ret = brick.send_direct_cmd(cmd, global_mem=1)
    return struct.unpack('<b', ret[5:])[0] > 0

brick = ev3.EV3(protocol='Usb', host='00:16:53:40:CE:B6')

tick = time.time()
print(test(brick, ev3.PORT_B + ev3.PORT_C, ev3.PORT_B, 54, 18))
print(time.time() - tick)
print(test(brick, ev3.PORT_D, ev3.PORT_D, 90, 45))
print(time.time() - tick)
print(test(brick, ev3.PORT_B + ev3.PORT_C, ev3.PORT_B, 54, 18))
print(time.time() - tick)
print(test(brick, ev3.PORT_D, ev3.PORT_D, 90, 45))
print(time.time() - tick)

