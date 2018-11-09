from socketserver import TCPServer
from core.web.handler import WebHandler


class WebServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def start(self):
        HOST, PORT = self.config['host'], self.config['port']
        TCPServer.allow_reuse_address = True
        self.logger.info('Starting server on {}:{}'.format(HOST, PORT))
        WebHandler.logger = self.logger
        self.server = TCPServer((HOST, PORT), WebHandler)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
