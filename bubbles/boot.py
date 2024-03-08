# VERSION 1.00
# URL https://raw.githubusercontent.com/Sumiza/micropython/beta/bubbles/boot.py
## URL https://raw.githubusercontent.com/Sumiza/micropython/main/bubbles/boot.py

"""
    work in progress but will be for tracking fermentation
"""

from machine import Pin, reset

dipswitch = dict()

for switch, pin in enumerate([10,11,12,13,14,15]):
    dipswitch[switch+1] = Pin(pin,Pin.IN,Pin.PULL_DOWN)

if dipswitch[1].value() == 1:
    from wifi import Wifi
    import localdata
    wifi = Wifi(localdata.SSID,
                localdata.PASSWORD,
                localdata.HOSTNAME,
                localdata.WIFILED,
                localdata.WIFITIMEOUT)
    wifi.connect()

    if wifi.isconnected():
        import settime
        settime.settime()

    if dipswitch[2].value() == 1 and wifi.isconnected():
        import update
        update.updateall()
    
    if dipswitch[6].value() == 1 and wifi.isconnected():
        import upload
        upload.run()
        reset()

if dipswitch[3].value() == 1:

    import time
    sensor = Pin(8, Pin.IN, Pin.PULL_DOWN)
    presstime = time.ticks_ms()
    counter = 0

    greenled  = Pin(9,Pin.OUT,value=0)

    def bubble(pin):
        global presstime
        global counter
        
        if time.ticks_diff(time.ticks_ms(),presstime) > 1000:
            presstime = time.ticks_ms()
            counter += 1
            greenled.on()
            print(pin,presstime)

    sensor.irq(trigger=Pin.IRQ_FALLING, handler=bubble)

    while True:
        time.sleep(1)
        greenled.off()

    

