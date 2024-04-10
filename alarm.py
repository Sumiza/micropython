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
            self.users = localdata.USERS
            self.sensors = localdata.SENSORS
            self.beeppin = localdata.BEEPPIN
            self.greenled = localdata.GREENLED
            self.redled = localdata.REDLED
            self.hornpin = localdata.HORNPIN
            self.pintime = localdata.PINTIME
            self.posturl = localdata.POSTURL
            self.postheaders = localdata.POSTHEADERS
            self.fromnumber = localdata.FROMNUMBER
            self.telnyxcallid = localdata.TELNYXCALLID
            self.alarmaudio = localdata.ALARMAUDIO

        async def ledgreen(self, toggle):
            if toggle is False:
                Pin(self.greenled,value=0)
            elif toggle is True:
                self.ledred(False)
                Pin(self.greenled,value=1)

        async def ledred(self,toggle=None):
            if toggle is False:
                Pin(self.redled,value=0)
            elif toggle is True:
                self.ledgreen(False)
                Pin(self.redled,value=1)

        async def arm(self,keypass,armtype):
            await asyncio.sleep(0.2) # wait for keypad to finish
            for _ in range(self.pintime):
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
            # disarm Done
        
        async def writestate(self,arm,keypass,armtype):
            now = time.localtime()
            humantime =  f'{now[3]}:{now[4]} {now[1]}/{now[2]}/{now[0]}' #TODO micropython version?
            self.last = f'Alarm {arm} by {self.users[keypass]} at {humantime} via {armtype}'
            with open('last','r') as file:
                file.write(self.last)

        async def notifyadmins(self):
            for values in self.users.values():
                if values['Admin'] is True:
                    await self.sendmessage(self.last,values['Phonenr'])

        async def trigger(self,whichpin):
            self.beep(True)
            for _ in range(self.pintime):
                if self.armed is True:
                    asyncio.sleep(1)
                else:
                    return # disarmed
            sendevery = 0
            while self.armed is True:
                Pin(self.hornpin,value = 1)
                sendevery -= 1
                if sendevery <= 0:
                    asyncio.create_task(self.sendalarm(whichpin))
                await asyncio.sleep(1)
            Pin(self.hornpin,value=0)
        
        async def sendalarm(self,whichpin):
            for values in self.users.values():
                if values['Admin'] is True:
                    await self.sendmessage(f"Alarm trigged on {whichpin}",values['Phonenr'])
                    await self.call(values['Phonenr'])
        
        async def sendmessage(self,message,number):
            message = {
                'from':self.fromnumber,
                'to':number,
                'text':message
            }
            try:
                await aiourlrequest.post(self.posturl+'messages',json=message,headers=self.postheaders,readlimit=50)
            except: pass

        async def call(self,number):
            message = {
                'from':self.fromnumber,
                'to':number,
                'connection_id':self.telnyxcallid,
                'time_limit_secs': 30,
                'audio_url': self.alarmaudio
            }
            try:
                await aiourlrequest.post(self.posturl+'calls',json=message,headers=self.postheaders,readlimit=50)
            except: pass
            
        def beep(self,toggle):
            if toggle is True:
                Pin(self.beeppin, value = 1)
            elif toggle is False:
                Pin(self.beeppin, value = 0)

        async def poolkeypad(self):
            curpass = ''
            while True:
                pushedkey = self.keypad.scan()
                if pushedkey:
                    self.beep(True)
                    while len(curpass) > 3:
                        curpass = curpass[1:]
                    curpass += pushedkey
                    if curpass in self.users:
                        if self.armed is False:
                            asyncio.create_task(self.arm(curpass,'keypad'))
                        elif self.armed is True:
                            asyncio.create_task(self.disarm(curpass,'keypad'))
                        curpass = ''
                    asyncio.sleep(0.1)
                    self.beep(False)
                asyncio.sleep(0.01)

        async def main(self):
            await asyncio.gather(
                self.poolkeypad()
                ) # run forever

alarm = Alarm('4x4')
asyncio.run(alarm.main())


        # async def armtoggle(self,keypass,armtype):
        #     if self.armed is False:
        #         self.arm(keypass,armtype)
        #     elif self.armed is True:
        #         self.disarm(keypass,armtype)
