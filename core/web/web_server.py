from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from core.web.routes import routes
from core.web.handler import Handler


class WebServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def start(self):
        HOST, PORT = "localhost", 8000
        TCPServer.allow_reuse_adress = True
        self.server = TCPServer((HOST, PORT), Handler)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
        finally:
            self.server.server_close()
