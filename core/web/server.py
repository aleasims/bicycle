import ssl
from socketserver import ThreadingMixIn
from http.server import HTTPServer
from core.web.handler import WebHandler


class ServerClass(ThreadingMixIn, HTTPServer):
    def get_request(self):
        sock, addr = self.socket.accept()
        if self.use_tls:
            sock = self.context.wrap_socket(sock, server_side=True)
        return sock, addr


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

        self.server.use_tls = config['use_tls']
        if config['use_tls']:
            self.server.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.server.context.load_cert_chain(config['certificate'], keyfile=config['keyfile'])

    def start(self):
        self.logger.info('Starting server on {}:{}'.format(self.server.server_name, self.server.server_port))
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
