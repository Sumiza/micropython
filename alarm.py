from machine import Pin, reset
import localdata

dipswitch = dict()

for switch, pin in enumerate([11,12,13,14]):
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
    
    if dipswitch[4].value() == 1 and wifi.isconnected():
        import upload
        upload.run()
        reset()

if dipswitch[3].value() == 1:
    import time
    import asyncio
    import aiourlrequest
    from matrixkeypad import MatrixKeypad

    level = 1
    def logger(data):
        if level is None or level == 0:
            return
        elif level == 1:
            print(data)

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
            logger(f"ledgreen {toggle}")
            if toggle is True:
                self.ledred(False)
                self.greenled.value(1)
            elif toggle is False:
                self.greenled.value(0)

        def ledred(self,toggle):
            logger(f"ledred {toggle}")
            if toggle is True:
                self.ledgreen(False)
                self.redled.value(1)
            elif toggle is False:
                self.redled.value(0)
                
        def beep(self,toggle):
            logger(f"beep {toggle}")
            if toggle is True:
                self.beeppin.value(1)
            elif toggle is False:
                self.beeppin.value(0)
    
        async def arm(self,keypass,armtype):
            logger(f'arm {keypass} {armtype}')
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
            logger(f'disarm {keypass} {armtype}')
            self.armed = False
            self.ledgreen(True)
            self.beep(False)
            self.writestate('Disarmed',keypass,armtype)
            self.notifyadmins()
            # Disarm Done
        
        def writestate(self,arm,keypass,armtype):
            now = time.localtime()
            humantime =  f'{now[3]:02d}:{now[4]:02d} {now[1]:02d}/{now[2]:02d}/{now[0]}'
            self.last = f'Alarm {arm} by {localdata.USERS[keypass]['Name']} at {humantime} via {armtype}'
            logger(f'writestate {self.last}')
            with open('last','w') as file:
                file.write(self.last)

        async def notifyadmins(self):
            for values in localdata.USERS.values():
                if values['Admin'] is True:
                    await self.sendmessage(self.last,values['Phonenr'])

        async def trigger(self,whichpin):
            logger(f'trigger {whichpin}')
            self.beep(True)
            for _ in range(localdata.PINTIME):
                if self.armed is True:
                    await asyncio.sleep(1)
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
            logger(f'trigger sendmessage {message} {number}')
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
            logger(f'trigger call {number}')
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
            logger('Starting doording')
            while True:
                if self.armed is False:
                    if self.sensorpins[localdata.DOORDING].value() == 0 and doortoggle is False:
                        logger(f'door opened {self.sensorpins[localdata.DOORDING].value()} {doortoggle}')
                        doortoggle = True
                        for _ in range(4):
                            self.beep(True)
                            await asyncio.sleep(0.1)
                            self.beep(False)
                            await asyncio.sleep(0.1)
                    elif self.sensorpins[localdata.DOORDING].value() == 1 and doortoggle is True:
                        logger(f'door closed {self.sensorpins[localdata.DOORDING].value()} {doortoggle}')
                        doortoggle = False
                await asyncio.sleep(1)

        async def checksensors(self):
            logger('Starting checksensor')
            while True:
                if self.armed is True:
                    respin = self.scansensors()
                    if respin is not None and self.armed is True:
                        await self.trigger(respin)
                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(1)

        async def poolkeypad(self):
            curpass = ''
            while True:
                pushedkey = self.keypad.scan()
                if pushedkey is not None:
                    logger(f'pushed key {pushedkey} - curpass: {curpass}')
                    self.beep(True)
                    while len(curpass) > 3:
                        curpass = curpass[1:]
                    curpass += str(pushedkey)
                    if curpass in localdata.USERS:
                        if self.armed is False:
                            asyncio.create_task(self.arm(int(curpass),'keypad'))
                        elif self.armed is True:
                            asyncio.create_task(self.disarm(int(curpass),'keypad'))
                        curpass = ''
                    await asyncio.sleep(0.5)
                    self.beep(False)
                await asyncio.sleep(0.01)
        
        async def getsms():

            def parsesms(message:str) -> dict:
                parseresponse = dict() 
                splitmess = message.split()
                try:
                    parseresponse['passkey'] = int(splitmess.pop(0))
                    parseresponse['action'] = splitmess.pop(0)
                    
                except: return None

            while True:
                await asyncio.sleep(30)
                try:
                    res = await aiourlrequest.get(localdata.TELNYXGETURL)
                    res = res.json()
                    res = res.get('content',None)
                    if res:
                        fromnr = res['data']['payload']['from']['phone_number']
                        message = res['data']['payload']['text']
                except: pass
                else:
                    if res:
                        for passkey, values in localdata.USERS.items():
                            if values['Admin'] is not True:
                                continue
                            if values['Phonenr'] != fromnr:
                                continue
                            parsed = parsesms(message)
            
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

            logger(f"Starting {self.armed}")

            running = list()
            running.append(asyncio.create_task(self.poolkeypad()))
            running.append(asyncio.create_task(self.checksensors()))
            if localdata.DOORDING is not None:
                running.append(asyncio.create_task(self.doording()))
            
            while True:
                for task in running:
                    if task.done():
                        logger(f'{task} reset needed')
                        reset() # something went very wrong
                await asyncio.sleep(5)

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
