# VERSION 1.01
# URL https://raw.githubusercontent.com/Sumiza/micropython/main/update.py
# This is not recommended to use as it is a security risk

import urequests
import os

def updateall(retry=1):
    didupdate = False
    for allfiles in os.listdir():
        if not allfiles.endswith('.py'):
            continue
        oldversion = None
        url = None
        with open(allfiles,'r') as file:
            for line in file.readlines():
                try:
                    if line.startswith('# VERSION'):
                        oldversion = float(line.replace('# VERSION','').strip())
                except Exception as e:
                    print('Version Error on current file',e,allfiles)
                if line.startswith('# URL'):
                    url = line.replace('# URL','').strip()
                    break

        if oldversion and url:
            newversion = None
            for _ in range(retry):
                try:
                    newfile = urequests.get(url,timeout=20)
                except Exception as e:
                    print('Download Error',e)
                    continue
                for line in newfile.text.splitlines():
                    if line.startswith('# VERSION'):
                        try:
                            newversion = float(line.replace('# VERSION','').strip())
                        except Exception as e:
                            print('Version Error on new file',e)
                        
            if newversion and newversion > oldversion:
                with open(allfiles,'w') as file:
                    print(f'Updating file {allfiles} to version {newversion} from {oldversion}.')
                    file.write(newfile.text)
                    didupdate = True

            newfile.close()
    if didupdate:
        import machine
        machine.reset()
