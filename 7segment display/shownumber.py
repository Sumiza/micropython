
import _thread
import time
from machine import Pin
import machine
machine.reset()
# from builtins import range
Pin(45,Pin.IN,Pin.PULL_UP)

class Shownumber():
    def __init__(self) -> None:
        self.number = '8888'
        
        self.inpins = [2,4,5,12]
        self.outpins = [23,22,14,18,19,25,13,15] #,15 is dot
        self.offpins()
        self.numbers = (
                        [1,1,1,1,1,1,0],
                        [0,1,1,0,0,0,0],
                        [1,1,0,1,1,0,1],
                        [1,1,1,1,0,0,1],
                        [0,1,1,0,0,1,1],
                        [1,0,1,1,0,1,1],
                        [1,0,1,1,1,1,1],
                        [1,1,1,0,0,0,0],
                        [1,1,1,1,1,1,1],
                        [1,1,1,1,0,1,1],
                        [0,0,0,0,0,0,0])
            
        _thread.start_new_thread(self.spawn,())
        
    def offpins(self):
        
        for inpin in self.inpins:
            Pin(inpin,Pin.IN,Pin.PULL_UP)
        
        for outpin in self.outpins:
            Pin(outpin,Pin.OUT,value=0)
            
    def show(self,number:str):
        if number:
            number = str(number)
            if number.isdigit() and len(number) <= 4:
                self.number = "% 4s" % number
            else:
                self.number = '0000'
        else:
            self.number = None
        
    def spawn(self):
        while True:
            if self.number:
                for lo, c in enumerate(self.number):
                    Pin(self.inpins[lo],Pin.IN,Pin.PULL_DOWN)
                    if c == ' ': c = 10
                    for loc ,nr in enumerate(self.numbers[int(c)]):
                        if nr == 1:
                            Pin(self.outpins[loc],Pin.OUT,value=nr)
                            time.sleep(0.001)
                            Pin(self.outpins[loc],Pin.OUT,value=0)
                    Pin(self.inpins[lo],Pin.IN,Pin.PULL_UP)
        else:
            self.offpins()
            _thread.exit()
