# VERSION 1.01
# URL https://raw.githubusercontent.com/Sumiza/micropython/main/wifi.py
import network
import time
import _thread
from machine import Pin
 
 
class Wifi():
    def __init__(self,ssid=None,password=None,hostname=None,wifipin=2,timeout=10,keepactive=True) -> None:
        self.ssid = ssid
        self.password = password
        self.wifipin = wifipin
        self.timeout = timeout
        self.keepactive = keepactive
        self.wifiled = Pin(self.wifipin ,Pin.OUT)
        self.wlan = network.WLAN(network.STA_IF)
        if hostname:
            network.hostname(hostname)
 
    def _connected(self):
        if self.wlan.isconnected():
            self.wifiled.on()
            return True
        else:
            self.wifiled.off()
            return False
 
    def _makecon(self):
        if not self._connected():
            self.wlan.active(True)
            try:
                self.wlan.connect(self.ssid,self.password)
            except: pass
            self._connected()
 
    def connect(self,ssid=None,password=None):
        self.ssid = ssid
        self.password = password
 
        if ssid is None: # off
            self.wlan.active(False)
            self._connected()
            return False
 
        if self.keepactive:
            _thread.start_new_thread(self._keepcon,(self.keepactive,))
 
        if ssid: # on
            if self.timeout:
                for _ in range(self.timeout):
                    self._makecon()
                    if not self._connected():
                        time.sleep(1)
                    else:
                        print(self.wlan.ifconfig())
                        return True
                return False
 
 
            else:
                while True:
                    if not self._connected():
                        self._makecon()
                        time.sleep(1)
                    else:
                        print(self.wlan.ifconfig())
                        return True
 
    def _keepcon(self,keepactive):
        while True:
            if self.ssid is None:
                break
            if not self._connected():
                self._makecon()
                time.sleep(1)
            else:
                time.sleep(10)
 
    def scan(self):
        return self.wlan.scan()
