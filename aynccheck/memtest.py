import asyncio
import aiourlrequest
import gc
import json

url = 'https://webhookbin.net/v1/bin/8c504643-ab30-4f99-8715-e71583828493'

class LocalSettings():
    def __init__(self) -> None:
        with open('settings.json','r') as file:
            jfile = json.loads(file.read())
            jfile:dict
            self.SSID = jfile.get('wifissid')
            self.PASSWORD = jfile.get('wifipass')
            self.HOSTNAME = jfile.get('wifihostname')
            self.WIFILED = jfile.get('wifiled')
            self.WIFITIMEOUT = jfile.get('wifitimeout')

            self.SENSORS = jfile.get('sensors')
            self.GREENLED = jfile.get('greenled')
            self.REDLED = jfile.get('redled')
            self.BEEPPIN = jfile.get('beeppin')
            self.HORNPIN = jfile.get('hornpin')
            self.PINTIME = jfile.get('pintime')
            self.DOORDING = jfile.get('doording')
            self.USERS = jfile.get('users')
            self.KEYPAD = jfile.get('keypad')

            self.TELNYXFROMNUMBER = jfile.get('telyxfromnumber')
            self.TELNYXCALLID = jfile.get('telnyxcallid')
            self.ALARMAUDIO = jfile.get('telnyxalarmaudio')
            self.TELNYXPOSTURL = jfile.get('telnyxposturl')
            self.TELNYXTOKEN = jfile.get('telnyxbearer')
            self.TELNYXPOSTHEADER = {'Authorization': self.TELNYXTOKEN}
            self.TELNYXGETURL = jfile.get('telnyxgeturl')

localdata = LocalSettings()

from wifi import Wifi
wifi = Wifi(localdata.SSID,
            localdata.PASSWORD,
            localdata.HOSTNAME,
            localdata.WIFILED,
            localdata.WIFITIMEOUT)
wifi.connect()
wifi.timeout = 0

if wifi.isconnected():
    try:
        import settime
        settime.settime(retry = 5, backup = True)
    except: pass # dont need time

async def getsms():
    while True:
        checksleep = 10
        if wifi.connect() is False:
            continue
        try:
            res = await aiourlrequest.aiourlrequest(url)
            res = res.json()
            res = res.get('content',None)
            print(res)
            if res is None:
                continue
            checksleep = 1

        except Exception as e:
            print(e) # connection and json issues
        finally:
            gc.collect()
            await asyncio.sleep(checksleep)

async def main():

    running = list()
    running.append(asyncio.create_task(getsms()))
    while True:
        for task in running:
            if task.done():
                print(f'{task} reset needed')
                # reset() # something went very wrong
        await asyncio.sleep(5)

asyncio.run(main())
