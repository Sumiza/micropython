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

    class Alarm():
        def __init__(self,keytype) -> None:
            self.armed = None
            self.last = None
            self.keypad = MatrixKeypad(keytype)

            #set pins
            self.sensorpins = {sensor:Pin(sensor,Pin.IN,Pin.PULL_DOWN) for sensor in localdata.SENSORS}
            self.greenled = Pin(localdata.GREENLED,Pin.OUT,value=0)
            self.redled = Pin(localdata.REDLED,Pin.OUT,value=0)
            self.beeppin = Pin(localdata.BEEPPIN,Pin.OUT,value=0)
            self.hornpin = Pin(localdata.HORNPIN,Pin.OUT,value=0)

        def ledgreen(self, toggle):
            if toggle is True:
                self.ledred(False)
                self.greenled.value(1)
            elif toggle is False:
                self.greenled.value(0)

        def ledred(self,toggle):
            if toggle is True:
                self.ledgreen(False)
                self.redled.value(1)
            elif toggle is False:
                self.redled.value(0)
                
        def beep(self,toggle):
            if toggle is True:
                self.beeppin.value(1)
            elif toggle is False:
                self.beeppin.value(0)
    
        async def arm(self,keypass,armtype):
            await asyncio.sleep(0.2) # wait for keypad to finish
            for _ in range(localdata.PINTIME):
                if self.armed is False:
                    self.beep(True)
                    self.ledgreen(True)
                    await asyncio.sleep(0.5)
                    self.beep(False)
                    self.ledgreen(False)
                    await asyncio.sleep(0.5)
                else:
                    return #stopped arming
            
            self.armed = True
            self.ledred(True)
            self.writestate('Armed',keypass,armtype)
            self.notifyadmins()
            # Arming Done
        
        async def disarm(self,keypass,armtype):
            self.armed = False
            self.ledgreen(True)
            self.beep(False)
            self.writestate('Disarmed',keypass,armtype)
            self.notifyadmins()
            # Disarm Done
        
        def writestate(self,arm,keypass,armtype):
            now = time.localtime()
            humantime =  f'{now[3]}:{now[4]} {now[1]}/{now[2]}/{now[0]}' #TODO micropython version?
            self.last = f'Alarm {arm} by {localdata.USERS[keypass]} at {humantime} via {armtype}'
            with open('last','w') as file:
                file.write(self.last)

        async def notifyadmins(self):
            for values in localdata.USERS.values():
                if values['Admin'] is True:
                    await self.sendmessage(self.last,values['Phonenr'])

        async def trigger(self,whichpin):
            self.beep(True)
            for _ in range(localdata.PINTIME):
                if self.armed is True:
                    asyncio.sleep(1)
                else:
                    return # disarmed
            sendevery = 0
            while self.armed is True:
                self.hornpin.value(1)
                sendevery -= 1
                if sendevery <= 0:
                    asyncio.create_task(self.sendalarm(whichpin))
                await asyncio.sleep(1)
            self.hornpin.value(0)
        
        async def sendalarm(self,whichpin):
            for values in localdata.USERS.values():
                if values['Admin'] is True:
                    await self.sendmessage(f"Alarm trigged on {whichpin}",values['Phonenr'])
                    await self.call(values['Phonenr'])
        
        async def sendmessage(self,message,number):
            message = {
                'from':localdata.FROMNUMBER,
                'to':number,
                'text':message
            }
            try:
                await aiourlrequest.post(
                    localdata.POSTURL+'messages',
                    json=message,
                    headers=localdata.POSTHEADERS,
                    readlimit=50)
            except: pass

        async def call(self,number):
            message = {
                'from':localdata.FROMNUMBER,
                'to':number,
                'connection_id':localdata.TELNYXCALLID,
                'time_limit_secs': 30,
                'audio_url': localdata.ALARMAUDIO
            }
            try:
                await aiourlrequest.post(
                    localdata.POSTURL+'calls',
                    json=message,
                    headers=localdata.POSTHEADERS,
                    readlimit=50)
            except: pass
        
        def scansensors(self) -> None|int:
            for pin, pinvalue in self.sensorpins.items():
                if pinvalue.value() == 1:
                    return pin
        
        async def doording(self):
            doortoggle = False
            while True:
                if self.armed is False:
                    if self.sensorpins[localdata.DOORDING].value() == 0 and doortoggle is False:
                        doortoggle = True
                        for _ in range(4):
                            self.beep(True)
                            asyncio.sleep(0.1)
                            self.beep(False)
                            asyncio.sleep(0.1)
                    elif self.sensorpins[localdata.DOORDING].value() == 1 and doortoggle is True:
                        doortoggle = False
                    asyncio.sleep(0.5)
                else:
                    asyncio.sleep(1)

        async def checksensors(self):
            while True:
                if self.armed is True:
                    respin = self.scansensors()
                    if respin is not None and self.armed is True:
                        await self.trigger(respin)
                    asyncio.sleep(0.1)
                else:
                    asyncio.sleep(1)

        async def poolkeypad(self):
            curpass = ''
            while True:
                pushedkey = self.keypad.scan()
                if pushedkey is not None:
                    self.beep(True)
                    while len(curpass) > 3:
                        curpass = curpass[1:]
                    curpass += pushedkey
                    if curpass in localdata.USERS:
                        if self.armed is False:
                            asyncio.create_task(self.arm(curpass,'keypad'))
                        elif self.armed is True:
                            asyncio.create_task(self.disarm(curpass,'keypad'))
                        curpass = ''
                    asyncio.sleep(0.1)
                    self.beep(False)
                asyncio.sleep(0.01)

        async def main(self):
            try:
                with open('last','r') as file:
                    laststatus = file.read().split()[1]
                    if laststatus == 'Armed':
                        self.armed = True
                        self.ledred(True)
                    elif laststatus == 'Disarmed':
                        self.armed = False
                        self.ledgreen(True)
            except: self.armed = False # first run with no last file

            running = list()
            running.append(asyncio.create_task(self.poolkeypad()))
            running.append(asyncio.create_task(self.checksensors()))
            if localdata.DOORDING is not None:
                running.append(asyncio.create_task(self.doording()))
            
            while True:
                for task in running:
                    if task.done():
                        ... # something went very wrong
                
                asyncio.sleep(5)

            # poolkey.done()
            # runme = [self.poolkeypad()]
            # await asyncio.gather(
            #     self.poolkeypad()
            #     ) # run forever

alarm = Alarm('4x4')
asyncio.run(alarm.main())


        # async def armtoggle(self,keypass,armtype):
        #     if self.armed is False:
        #         self.arm(keypass,armtype)
        #     elif self.armed is True:
        #         self.disarm(keypass,armtype)
