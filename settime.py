
# from urlrequest import UrlRequest as urequest

import urlrequest
import time
import machine

a = urequest.get('https://worldtimeapi.org/api/ip').json()

print(a)



curtime = a['unixtime']+a['raw_offset']+a['dst_offset']

if time.gmtime(0)[0] == 2000:
    curtime = curtime - 946684800


print(curtime)

tt = time.gmtime(curtime)

print(tt)
machine.RTC.datetime(tt)
