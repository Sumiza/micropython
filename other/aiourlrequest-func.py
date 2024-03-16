
import json as jsonclass
import asyncio

"""
    async urlrequest in a class to make it easier to use
"""
                
async def urlrequest(
                url:str,
                data:str = None,
                json = None,
                method:str = 'GET',
                headers:dict = None,
                readlimit:int = 500,
                timeout:float = 10 #TODO
                ):

    if headers is None:
        headers = {}

    try:
        proto, _, host, path = url.split("/", 3)
    except ValueError:
        proto, _, host = url.split("/", 2)
        path = ""
    
    headers['HOST'] = host

    if not headers.get('User-Agent'):
        headers['User-Agent'] = 'aioUrlRequest v1.0'

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
    
    if proto == "http:":
        port = 80
        ssl = False
    elif proto == "https:":
        port = 443
        ssl = True
    else:
        raise ValueError("Unsupported: " + proto)

    reader, writer = await asyncio.open_connection(host, port, ssl=ssl)
    query = f'{method} /{path} HTTP/1.1\r\n{headers}{data}\r\n\r\n'.encode()
    writer.write(query)
    await writer.drain()
    
    response = dict()
    firstline = await reader.readline()
    firstline = firstline.decode().split(' ')
    response['status_code'] = firstline[1]
    response['status'] = firstline[2]
    
    while True:
        line = await reader.readline()
        if line == b'' or line ==b'\r\n':
            break
        line = line.decode().split(':')
        response[line[0]] = ''.join(line[1:]).strip()
          
    resdata = await reader.read(readlimit)
    response['data'] = resdata.decode()
    writer.close()

    return response

async def test():
    #from aiourlrequest import urlrequest
    a = await urlrequest('https://webhookbin.net/v1/makebin',
                         method='GET',
                         data='',
                         headers={'jumping':"cow"})
    print(a)
    print(a.get('data'))

if __name__ == '__main__':
    asyncio.run(test())