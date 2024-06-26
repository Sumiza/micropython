
"""
    Boot template
"""

from machine import Pin, reset

dipswitch = dict()

for switch, pin in enumerate([10,11,12,13,14,15]):
    dipswitch[switch+1] = Pin(pin,Pin.IN,Pin.PULL_UP) #pin to ground

if dipswitch[1].value() == 0:
    from wifi import Wifi
    import localdata
    wifi = Wifi(localdata.SSID,
                localdata.PASSWORD,
                localdata.HOSTNAME,
                localdata.WIFILED,
                localdata.WIFITIMEOUT)
    wifi.connect()

    if wifi.isconnected():
        try:
            import settime
            settime.settime(5)
        except:
            pass # dont need time

    if dipswitch[2].value() == 0 and wifi.isconnected():
        import update
        update.updateall()
    
    if dipswitch[6].value() == 0 and wifi.isconnected():
        import upload
        upload.run()
        reset()

if dipswitch[3].value() == 0:
    ...

    

