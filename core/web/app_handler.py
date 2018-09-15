from http.server import BaseHTTPRequestHandler
from core.web.routes import routes
from http import HTTPStatus
import os

class AppHandler(BaseHTTPRequestHandler):
    html = list(routes['static']['html'].keys())
    js = list(routes['static']['js'].keys())

    def __init__(self, request, client_address, server, logger, static_dir='www'):
        self.static_dir = static_dir
        self.logger = logger
        super().__init__(request, client_address, server)

    def do_GET(self):
        self.response()
        
    def response(self):
        status = HTTPStatus.NOT_FOUND
        content_type = 'text/plain'
        local_path = None
        if self.path in self.html + self.js:
            status = HTTPStatus.OK
            if self.path in self.js:
                local_path = os.path.join(self.static_dir, 'js', routes['static']['js'][self.path])
                content_type = 'text/javascript'
            if self.path in self.html:
                local_path = os.path.join(self.static_dir, 'html', routes['static']['html'][self.path])
                content_type = 'text/html'

        self.send_response(status.value,
                           status.phrase)    
        self.send_header('Content-type', content_type)
        self.send_body(local_path)

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