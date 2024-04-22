# VERSION 1.03
# URL https://raw.githubusercontent.com/Sumiza/micropython/main/wifi.py
 
import network
import time
from machine import Pin
 
class Wifi():
    def __init__(self,ssid=None,password=None,hostname=None,wifipin=None,timeout=10) -> None:
 
        self.ssid = ssid
        self.password = password
        self.timeout = timeout
        self.wlan = network.WLAN(network.STA_IF)
 
        if wifipin:
            self.wifiled = Pin(wifipin ,Pin.OUT)
        else:
            self.wifiled = None
 
        if hostname:
            network.hostname(hostname)
 
    def led(self,onoff=None,selfcheck=False):
 
        if self.wifiled is not None:
            if selfcheck:
                onoff = self.wlan.isconnected()
 
            if onoff:
                self.wifiled.on()
            else:
                self.wifiled.off()
 
    def connect(self,ssid=None,password=None):

        if (ssid is None and 
            password is None and 
            self.isconnected() is True):
            return True
 
        if self.ssid is None:
            self.ssid = ssid
        if self.password is None:
            self.password = password
 
        if self.ssid is None:
            raise ValueError('SSID is needed')
 
        self.wlan.active(True)
        self.wlan.connect(self.ssid,self.password)
 
        for _ in range(self.timeout):
            if self.wlan.isconnected():
                print(self.wlan.ifconfig())
                self.led(True)
                return True
            else:
                time.sleep(1)
        self.led(False)
        return False
 
    def disconnect(self):
        self.wlan.active(False)
        self.wlan.disconnect()
        self.led(False)
        return True
 
    def deinit(self):
        # Raspberry pi pico W only
        self.led(False)
        self.wlan.deinit()
        return True
 
    def isconnected(self):
        connected = self.wlan.isconnected()
        self.led(onoff=connected)
        return connected
 
    def scan(self):
        return self.wlan.scan()