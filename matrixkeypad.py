
import asyncio
import machine

keypad4x4 = {'pad':[
    [1,  2,  3,  'A'],
    [4,  5,  6,  'B'],
    [7,  8,  9,  'C'],
    ['*',0,  '#','D']],
    'column':[3,2,1,0],
    'row':[7,6,5,4]}
keypad3x4 = {'pad':[
    [1,  2,  3],
    [4,  5,  6],
    [7,  8,  9],
    ['*',0,  '#']],
    'column':[2,1,0],
    'row':[6,5,4,3]}

class MatrixKeypad():
    def __init__(self,padtype) -> None:
        self.padtype = padtype

        if self.padtype == '4x4':
            self.keypad = keypad4x4
        elif self.padtype == '3x4':
            self.keypad = keypad3x4
        else: ValueError('Keypad type needed 4x4 or 3x4')
        
        self.col = []
        for col in self.keypad['column']:
            self.col.append(machine.Pin(col,machine.Pin.OUT,value=0))

        self.row = []
        for row in self.keypad['row']:
            self.row.append(machine.Pin(row,machine.Pin.IN,machine.Pin.PULL_DOWN))

    def scan(self):
        pushed = None

        for colnr, col in enumerate(self.col):
            col:machine.Pin
            col.value(1)

            for rownr, row in enumerate(self.row):
                row:machine.Pin
                if row.value() == 1:
                    pushed = self.keypad['pad'][rownr][colnr]
                    break
            col.value(0)
            if pushed is not None:
                return pushed

    async def scan_async(self):
            pushed = None

            for colnr, col in enumerate(self.col):
                col:machine.Pin
                col.value(1)

                for rownr, row in enumerate(self.row):
                    row:machine.Pin
                    if row.value() == 1:
                        pushed = self.keypad['pad'][rownr][colnr]
                        break
                    asyncio.sleep(0)
                col.value(0)
                if pushed is not None:
                    return pushed