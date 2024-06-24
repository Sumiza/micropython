# VERSION 1.03
# URL https://raw.githubusercontent.com/Sumiza/micropython/main/aiourlrequest.py

import json as jsonclass
import asyncio

"""
    mostly a drop in replacement for requests 
    but async for very simple tasks
    ssl still blocks on sending ? 
    import aiourlrequest as requests
"""

class Response():
    def __init__(self) -> None:
        self.text = None
        self.status_code = None
        self.status = None
        self.data  = b''
        self.headers = dict()

    def json(self):
        return jsonclass.loads(self.text)
    
    def __str__(self) -> str:
        return self.status_code

async def aiourlrequest(
                url:str,
                data:str = None,
                json = None,
                method:str = 'GET',
                headers:dict = None,
                readlimit:int = 5000,
                ssl = None,
                timeout:float = 10
                ):

    if headers is None:
        headers = {}

    try:
        proto, _, host, path = url.split("/", 3)
    except ValueError:
        proto, _, host = url.split("/", 2)
        path = ""
    
    headers['HOST'] = host
    headers['Connection'] = 'Close' # close connection when done or reader can hang

    if not headers.get('User-Agent'):
        headers['User-Agent'] = 'aioUrlRequest v1.03'

    if json:
        headers['Content-Type'] = 'application/json'
        data = jsonclass.dumps(json)
    
    if data:
        headers["Content-Length"] = len(data)
        data = '\r\n' + data
    else:
        data = ''

    for key,value in headers.items(): # prevent sending of None types and such
        if not isinstance(value,str):
            headers[key] = str(value)

    headers = "\r\n".join(f"{k}: {v}" for k, v in headers.items()) + "\r\n"
    
    if ssl is None:
        if proto == "http:":
            port = 80
            ssl = False
        elif proto == "https:":
            port = 443
            ssl = True # blocking?
        else:
            raise ValueError("Unsupported: " + proto)

    reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port, ssl=ssl),timeout)
    query = f'{method} /{path} HTTP/1.1\r\n{headers}{data}\r\n\r\n'.encode()
    writer.write(query)
    await asyncio.wait_for(writer.drain(),timeout)

    firstline = await asyncio.wait_for(reader.readline(),timeout)
    firstline = firstline.decode().split(' ')

    response = Response()
    response.status_code = firstline[1]
    response.status = firstline[2]

    while True:
        line = await asyncio.wait_for(reader.readline(),timeout)
        if line == b'' or line == b'\r\n':
            break
        line = line.decode().split(':')
        response.headers[line[0]] = ''.join(line[1:]).strip()
    
    while True:
        chunk = await asyncio.wait_for(reader.read(8),timeout)
        if chunk == b'':
            break
        if len(response.data) >= readlimit:
            break
        response.data += chunk

    try:
        response.text = response.data.decode()
    except:
        response.text = None
    writer.close()

    return response

async def get(url:str, data:str = None, json:dict = None, headers:dict = None, readlimit:int = 5000, ssl = None):
    return await aiourlrequest(url=url, data=data, json=json, headers=headers, readlimit=readlimit, ssl=ssl, method='GET')
async def post(url:str, data:str = None, json:dict = None, headers:dict = None, readlimit:int = 5000, ssl = None):
    return await aiourlrequest(url=url, data=data, json=json, headers=headers, readlimit=readlimit, ssl=ssl, method='POST')
async def put(url:str, data:str = None, json:dict = None, headers:dict = None, readlimit:int = 5000, ssl = None):
    return await aiourlrequest(url=url, data=data, json=json, headers=headers, readlimit=readlimit, ssl=ssl, method='PUT')
async def delete(url:str, data:str = None, json:dict = None, headers:dict = None, readlimit:int = 5000, ssl = None):
    return await aiourlrequest(url=url, data=data, json=json, headers=headers, readlimit=readlimit, ssl=ssl, method='DELETE')
async def head(url:str, data:str = None, json:dict = None, headers:dict = None, readlimit:int = 5000, ssl = None):
    return await aiourlrequest(url=url, data=data, json=json, headers=headers, readlimit=readlimit, ssl=ssl, method='HEAD')
async def patch(url:str, data:str = None, json:dict = None, headers:dict = None, readlimit:int = 5000, ssl = None):
    return await aiourlrequest(url=url, data=data, json=json, headers=headers, readlimit=readlimit, ssl=ssl, method='PATCH')

if __name__ == '__main__':
    async def demo():
        #import aiourlrequest as requests
        b = await aiourlrequest(
            'https://webhookbin.net/v1/makebin',
            data='',
            headers={'jumping':"cow"})
        
        print(b)
        print(b.json())
        print(b.text)
        print(b.headers)
    asyncio.run(demo())