from http.server import BaseHTTPRequestHandler
from core.routes import routes
from http import HTTPStatus
import os

class StaticHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, static_dir='/home/alea/bicycle/www/html'):
        self.static_dir = static_dir
        super().__init__(request, client_address, server)

    def do_GET(self):
        if not self.exists(self.path):
            self.send_NOT_FOUND()
            return False
        self.response()

    def response(self):
        self.send_response(HTTPStatus.OK.value,
                               HTTPStatus.OK.phrase)
        content_type = 'text/html'
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.send_body()

    def send_body(self):
        path = os.path.join(self.static_dir, routes['static']['html'][self.path]) 
        f = open(path, 'rb')
        content = f.read()
        self.wfile.write(content)

    def send_NOT_FOUND(self):
        self.send_response(HTTPStatus.NOT_FOUND.value,
                               HTTPStatus.NOT_FOUND.phrase)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html>Not found</html>')

    def exists(self, path):
        html = list(routes['static']['html'].keys())
        js = list(routes['static']['js'].keys())
        return path in html + js
