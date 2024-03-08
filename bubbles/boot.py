
from machine import Pin, reset

pinswitch = dict()

for switch, pin in enumerate([10,11,12,13,14,15]):
    pinswitch[switch+1] = Pin(pin,Pin.IN,Pin.PULL_DOWN)

if pinswitch[1].value() == 1:
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

    if pinswitch[2].value() == 1 and wifi.isconnected():
        import update
        update.updateall()
    
    if pinswitch[6].value() == 1 and wifi.isconnected():
        import upload
        upload.run()
        reset()

if pinswitch[3] == 1:
    print('program starts here')


print('Done')
    

