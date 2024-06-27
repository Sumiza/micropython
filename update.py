# VERSION 1.04
# URL https://raw.githubusercontent.com/Sumiza/micropython/main/update.py
# This is not recommended to use as it is a security risk

import urequests
import os

def download(url,retry):
    for _ in range(retry):
        try:
            print('Checking',url)
            return urequests.get(url,timeout=10)
        except Exception as e:
            print('Download Error',e)
    return None
    
def updateall(retry=1):
    didupdate = False
    print('Checking if update is needed...')
    allfileslist = [f for f in os.listdir() if f.endswith('.py')]

    try:
        import localdata
        installfiles = localdata.INSTALLFILES
    except: pass # no install needed
    else:
        if installfiles:
            for url in installfiles:
                filename = url.split('/')[-1]
                if filename not in allfileslist:
                    newfile = download(url,retry)
                    if newfile:
                        with open(filename,'w') as file:
                            print(f'Downloaded {filename}')
                            file.write(newfile.text)
                            newfile.close()
    
    for allfiles in allfileslist:
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
            print(f'Local version of {allfiles} is {oldversion}')
            newversion = None
            newfile = download(url,retry)
            if newfile:
                for line in newfile.text.splitlines():
                    if line.startswith('# VERSION'):
                        try:
                            newversion = float(line.replace('# VERSION','').strip())
                            print(f'Remote version is {newversion}')
                            break
                        except Exception as e:
                            print('Version Error on new file',e,line)
                if newversion is None:
                    print('Failed to get new file')
                            
                if newversion and newversion > oldversion:
                    with open(allfiles,'w') as file:
                        print(f'Updating file {allfiles} to version {newversion} from {oldversion}.')
                        file.write(newfile.text)
                        didupdate = True
                newfile.close()

    if didupdate:
        import machine
        machine.reset()
    else:
        print('No updated needed running newest version(s)')
