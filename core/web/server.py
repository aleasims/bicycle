from socketserver import ThreadingMixIn
from http.server import HTTPServer
from core.web.handler import WebHandler


class ServerClass(ThreadingMixIn, HTTPServer):
    pass


class WebServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.HOST, self.PORT = config['host'], config['port']
        WebHandler.logger = self.logger
        self.server = ServerClass((self.HOST, self.PORT), WebHandler)
        self.server.allow_reuse_address = True
        self.server.version = config['version']
        self.server.www_dir = config['www_dir']

    def start(self):
        self.logger.info('Starting server on {}:{}'.format(self.server.server_name, self.server.server_port))
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
