

import asyncio
import aiourlrequest
from wifi import Wifi
from machine import Pin
import gc


wifi  = Wifi(
    ssid="",
    password="",
    wifipin=""
)
wifi.connect()

async def blink(led='LED',every=0.5):
    light = Pin(led,Pin.OUT)
    while True:
        light.toggle()
        await asyncio.sleep(every)

async def demo():
    while True:
        b = await aiourlrequest(
            'https://webhookbin.net/v1/makebin',
            data='',
            headers={'jumping':"cow"})
        
        print(b.text)
        # gc.collect()
        asyncio.sleep(5)

def runme():
    asyncio.create_task(blink())
    asyncio.run(demo())





# if __name__ == '__main__':
#     async def demo():
#         #import aiourlrequest as requests
#         b = await aiourlrequest(
#             'https://webhookbin.net/v1/makebin',
#             data='',
#             headers={'jumping':"cow"})
        
#         print(b)
#         print(b.json())
        
#         print(b.headers)
#     asyncio.run(demo())