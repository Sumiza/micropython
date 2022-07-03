import network
import time
import urequests
from machine import Pin
from shownumber import Shownumber
​
def connectwifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('', '')
        while not wlan.isconnected():
            time.sleep(10)
            print('failed to connect')
        else:
            print('network config:', wlan.ifconfig())
connectwifi()
​
def pinoff():
    pingreen.off()
    pinred.off()
    pinblue.off()
    
def greenon():
    pinoff()
    pingreen.on()
​
def redon():
    pinoff()
    pinred.on()
    
def blueon():
    pinoff()
    pinblue.on()
    
pingreen = Pin(32,Pin.OUT)
pinred = Pin(21,Pin.OUT)
pinblue = Pin(33,Pin.OUT)
cpin = Pin(35,Pin.IN,Pin.PULL_DOWN)
blueon()
​
btc = 0.00
oldbtc = 0.00
display = Shownumber()
while cpin.value() == 1:
    try:
        btcres = urequests.get('https://bitpay.com/api/rates/XAG/')
        btc = btcres.json()['rate']
        btcres.close()
        if btc > oldbtc:
            greenon()
        elif btc < oldbtc:
            redon()
        else:
            blueon()
        oldbtc = btc
        print(btc)
        display.show(int(btc))
    except:
        print("error")
        pinoff()
    time.sleep(60)
display.show(None)
pinoff()
