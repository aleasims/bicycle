from http.server import HTTPServer
from core.web.handler import WebHandler


class WebServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def start(self):
        HOST, PORT = self.config['host'], self.config['port']
        HTTPServer.allow_reuse_address = True
        HTTPServer.version = 'BicycleWEB/0.1b'
        HTTPServer.www_dir = '/home/alea/bicycle/www'
        self.logger.info('Starting server on {}:{}'.format(HOST, PORT))
        WebHandler.logger = self.logger
        self.server = HTTPServer((HOST, PORT), WebHandler)
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
