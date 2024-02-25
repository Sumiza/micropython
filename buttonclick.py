
# refrence not stand alone

import machine, time

button = machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_DOWN)

presstime = time.ticks_ms()

def press(pin):
    global presstime
    
    if time.ticks_diff(time.ticks_ms(),presstime) > 200:
        presstime = time.ticks_ms()
        print(pin,presstime)

button.irq(trigger=machine.Pin.IRQ_FALLING, handler=press)

while True:
    time.sleep(1)