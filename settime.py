# VERSION 1.003
# URL https://raw.githubusercontent.com/Sumiza/micropython/beta/settime.py
## URL https://raw.githubusercontent.com/Sumiza/micropython/main/settime.py

import urequests
import time
from machine import RTC


def settime(retry=1):
    resjson = None
    for _ in range(retry):
        try:
            resjson = urequests.get('https://worldtimeapi.org/api/ip').json()
        except Exception as e:
            print('Download Error',e)
    
    if resjson:
        curtime = resjson['unixtime']+resjson['raw_offset']+resjson['dst_offset']

        if time.gmtime(0)[0] == 2000:
            curtime = curtime - 946684800
        adjtime = time.gmtime(curtime)

        datetimetuple = (adjtime[0],adjtime[1],adjtime[2],0,adjtime[3],adjtime[4],adjtime[5],0)
        rtc = RTC()
        rtc.datetime(datetimetuple)
        print('Local time is:',time.localtime())
        return True
    return False
