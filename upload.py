# VERSION 1.00
## URL https://raw.githubusercontent.com/Sumiza/micropython/main/upload.py
# URL https://raw.githubusercontent.com/Sumiza/micropython/beta/upload.py
# This is not recommended to use as it is a security risk


from microdot import Microdot, send_file, Request

html='''
<!doctype html>
<html>
  <head>
    <title>Upload File</title>
    <meta charset="UTF-8">
  </head>
  <body>
    <h1>Upload File</h1>
    <form id="form">
      <input type="file" id="file" name="file" />
      <input type="submit" value="Upload" />
    </form>
    <button onclick="window.location.href='/shutdown';"> 
      Reboot
    </button>
    <script>
      async function upload(ev) {
        ev.preventDefault();
        const file = document.getElementById('file').files[0];
        if (!file) {
          return;
        }
        await fetch('/upload', {
          method: 'POST',
          body: file,
          headers: {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': `attachment; filename="${file.name}"`,
          },
        }).then(res => {
          console.log('Upload accepted');
          window.location.href = '/';
        });
      }
      document.getElementById('form').addEventListener('submit', upload);
    </script>
  </body>
</html>'''


app = Microdot()
Request.max_content_length = 1024 * 1024  # 1MB (change as needed)

@app.route('/')
async def index(request):
    return html, 200, {'Content-Type': 'text/html'}

@app.post('/upload')
async def upload(request):
    # obtain the filename and size from request headers
    filename = request.headers['Content-Disposition'].split(
        'filename=')[1].strip('"')
    size = int(request.headers['Content-Length'])

    # sanitize the filename
    filename = filename.replace('/', '_')

    # write the file to the files directory in 1K chunks
    with open(filename, 'wb') as f:
        while size > 0:
            chunk = await request.stream.read(min(size, 1024))
            f.write(chunk)
            size -= len(chunk)

    print('Successfully saved file: ' + filename)
    return ''

@app.route('/shutdown')
async def shutdown(request):
    request.app.shutdown()
    return 'The server is shutting down...'

def run(port=80,debug=True):
    app.run(debug=debug,port=port)

if __name__ == '__main__':
    app.run(debug=True)