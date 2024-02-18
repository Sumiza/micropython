
# from urlrequest import UrlRequest as urequest
import urequests
import time
from machine import RTC

a = urequests.get('https://worldtimeapi.org/api/ip').json()

print(a)



curtime = a['unixtime']+a['raw_offset']+a['dst_offset']

if time.gmtime(0)[0] == 2000:
    curtime = curtime - 946684800

print(curtime)

d = time.gmtime(curtime)

datetimetuple = (d[0],d[1],d[2],d[3],d[4],0,0)

print(datetimetuple)

rtc = RTC()

rtc.datetime(datetimetuple)
