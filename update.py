# VERSION 1.0
#
import urequests
import os

for allfiles in os.listdir():
    if not os.path.isfile(allfiles):
        continue
    oldversion = None
    url = None
    with open(allfiles,'r',1,'utf-8','ignore') as file:
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
            with open(allfiles,'w',1,'utf-8') as file:
                print(f'Updating file {allfiles} to version {newversion} from {oldversion}.')
                file.write(newfile.text)

        newfile.close()
