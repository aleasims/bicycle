import ssl
import json
from socketserver import ThreadingMixIn
from http.server import HTTPServer
from core.web import db
from core.web import view
from core.web import user
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
        self.host, self.port = config['host'], config['port']

        db.register_client(config['db_address'])
        self.logger.debug('Registered DB client for address {}'.format(config['db_address']))

        view.load_model(config['www_dir'])
        self.logger.debug('Page model loaded')

        scheme = 'https' if config['use_tls'] else 'http'
        host = scheme + '://' + config['domain']
        if self.port not in (80, 443):
            host = host + ':' + str(self.port)
        email = config['email']
        account = json.loads(open(email['account'], 'r', encoding='utf-8').read())
        user.register_verificator(host, email['mailhost'],
            email['port'], account['address'], account['password'])
        self.logger.debug('Verificator mailbox loaded')

        WebHandler.logger = self.logger
        self.server = ServerClass((self.host, self.port), WebHandler)
        self.server.allow_reuse_address = True
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
