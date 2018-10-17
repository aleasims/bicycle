from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from core.web.routes import routes
from core.web.handler import Handler


class WebServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def start(self):
        HOST, PORT = self.config['host'], self.config['port']
        TCPServer.allow_reuse_address = True
        self.logger.info('Starting server on {}:{}'.format(HOST, PORT))
        self.server = TCPServer((HOST, PORT), Handler)
        Handler.logger = self.logger
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
