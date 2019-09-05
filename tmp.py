import time
import ev3

HOST = '00:16:53:40:CE:B6'
remote = ev3.EV3(protocol='Usb', host=HOST)

def move(ports, deg):
    move = b''.join([
        ev3.opOutput_Step_Power,
        ev3.LCX(0),
        ev3.LCX(ports),
        ev3.LCX(100 if deg > 0 else -100),
        ev3.LCX(0),
        ev3.LCX(abs(deg)),
        ev3.LCX(0),
        ev3.LCX(1)
    ])
    remote.send_direct_cmd(move)

tick = time.time()
for _ in range(10):
    move(ev3.PORT_A + ev3.PORT_B, 54)
    time.sleep(.06)
    move(ev3.PORT_C + ev3.PORT_D, 54)
    time.sleep(.06)
print(time.time() - tick)

