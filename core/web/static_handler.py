from http.server import BaseHTTPRequestHandler
from core.routes import routes
from http import HTTPStatus
import os

class StaticHandler(BaseHTTPRequestHandler):
    html = list(routes['static']['html'].keys())
    js = list(routes['static']['js'].keys())

    def __init__(self, request, client_address, server, static_dir='/home/alea/bicycle/www'):
        self.static_dir = os.environ['BI_STATIC_DIR']
        super().__init__(request, client_address, server)

    def do_GET(self):
        self.response()
        
    def response(self):


    def send_body(self, local_path):
        content = bytearray()
        if local_path:
            f = open(local_path, 'rb')
            while True:
                buf = f.readline()
                if buf == b'':
                    break
                content += buf
        length = len(content)
        self.send_header('Content-length', length)
        self.end_headers()
        self.wfile.write(content)
