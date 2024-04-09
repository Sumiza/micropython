from machine import Pin, reset
import localdata

dipswitch = dict()

for switch, pin in enumerate([10,11,12,13,14,15]):
    dipswitch[switch+1] = Pin(pin,Pin.IN,Pin.PULL_DOWN)

if dipswitch[1].value() == 1:
    from wifi import Wifi
    wifi = Wifi(localdata.SSID,
                localdata.PASSWORD,
                localdata.HOSTNAME,
                localdata.WIFILED,
                localdata.WIFITIMEOUT)
    wifi.connect()

    if wifi.isconnected():
        try:
            import settime
            settime.settime()
        except:
            pass # dont need time

    if dipswitch[2].value() == 1 and wifi.isconnected():
        import update
        update.updateall()
    
    if dipswitch[6].value() == 1 and wifi.isconnected():
        import upload
        upload.run()
        reset()

if dipswitch[3].value() == 1:
    import time
    import asyncio
    import aiourlrequest
    from matrixkeypad import MatrixKeypad
    ARMED = False
    LAST = None
    
    keypad = MatrixKeypad('4x4')
    users = localdata.USERS
    admins = localdata.ADMINS
    sensors = localdata.SENSORS
    beeppin = localdata.BEEPPIN
    greenled = localdata.GREENLED
    redled = localdata.REDLED
    hornpin = localdata.HORNPIN
    pintime = localdata.PINTIME
    posturl = localdata.POSTURL
    postheaders = localdata.POSTHEADERS
    fromnumber = localdata.FROMNUMBER
    telnyxcallid = localdata.TELNYXCALLID
    alarmaudio = localdata.ALARMAUDIO

    async def ledgreen(toggle):
        if toggle is False:
            Pin(greenled,value=0)
        elif toggle is True:
            ledred(False)
            Pin(greenled,value=1)

    async def ledred(toggle=None):
        if toggle is False:
            Pin(redled,value=0)
        elif toggle is True:
            ledgreen(False)
            Pin(redled,value=1)

    async def arm(keypass,armtype):
        await asyncio.sleep(0.2) # wait for keypad to finish
        for _ in range(pintime):
            if ARMED is False:
                beep(True)
                ledgreen(True)
                await asyncio.sleep(0.5)
                beep(False)
                ledgreen(False)
                await asyncio.sleep(0.5)
            else:
                return #stopped arming
        
        ARMED = True
        ledred(True)
        writestate('Armed',keypass,armtype)
        notifyadmins()
        # Arming Done
    
    async def disarm(keypass,armtype):
        ARMED = False
        ledgreen(True)
        beep(False)
        writestate('Disarmed',keypass,armtype)
        notifyadmins()
        # disarm Done
    
    async def writestate(arm,keypass,armtype):
        now = time.localtime()
        humantime =  f'{now[3]}:{now[4]} {now[1]}/{now[2]}/{now[0]}'
        LAST = f'Alarm {arm} by {keypass['Name']} at {humantime()} via {armtype}'
        with open('last','r') as file:
            file.write(LAST)

    async def notifyadmins():
        for values in admins.values():
            await sendmessage(LAST,values['Phonenr'])

    async def trigger(whichpin):
        beep(True)
        for _ in range(pintime):
            if ARMED is True:
                asyncio.sleep(1)
            else:
                return # disarmed
        sendevery = 0
        while ARMED is True:
            Pin(hornpin,value = 1)
            sendevery -= 1
            if sendevery <= 0:
                asyncio.create_task(sendalarm(whichpin))
            await asyncio.sleep(1)
        Pin(hornpin,value=0)
    
    async def sendalarm(whichpin):
        for values in admins.values():
            await sendmessage(f"Alarm trigged on {whichpin}",values['Phonenr'])
            await call(values['Phonenr'])
    
    async def sendmessage(message,number):
        message = {
            'from':fromnumber,
            'to':number,
            'text':message
        }
        try:
            await aiourlrequest.post(posturl+'messages',json=message,headers=postheaders,readlimit=50)
        except: pass

    async def call(number):
        message = {
            'from':fromnumber,
            'to':number,
            'connection_id':telnyxcallid,
            'time_limit_secs': 30,
            'audio_url': alarmaudio
        }
        try:
            await aiourlrequest.post(posturl+'calls',json=message,headers=postheaders,readlimit=50)
        except: pass
        
    async def armtoggle(keypass,armtype):
        if ARMED is False:
            arm(keypass,armtype)
        elif ARMED is True:
            disarm(keypass,armtype)
    
    def beep(toggle):
        if toggle is True:
            Pin(beeppin,value = 1)
        elif toggle is False:
            Pin(beeppin, value = 0)

    async def poolkeypad():
        curpass = ''
        while True:
            pushedkey = keypad.scan()
            if pushedkey:
                beep(True)
                while len(curpass) > 3:
                    curpass = curpass[1:]
                curpass += pushedkey

                if curpass in users:
                    asyncio.create_task(armtoggle(curpass,'keypad'))
                    curpass = ''
                asyncio.sleep(0.1)
                beep(False)
    
            asyncio.sleep(0.01)

    async def main():
        await asyncio.gather(
            poolkeypad()
            ) # run forever

asyncio.run(main())
