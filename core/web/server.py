from socketserver import ThreadingMixIn
from http.server import HTTPServer
from core.web import db
from core.web import view
from core.web.handler import WebHandler


class ServerClass(ThreadingMixIn, HTTPServer):
    pass


class WebServer:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config
        self.host, self.port = config['host'], config['port']

        db.register_client(config['db_address'])
        self.logger.debug('Registered DB client for address {}'.format(config['db_address']))

        view.load_model(config['www_dir'])
        self.logger.debug('Page model loaded')

        WebHandler.logger = self.logger
        WebHandler.SESS_EXP_TIME = config['auth_session_exp_time']

        self.server = ServerClass((self.host, self.port), WebHandler)
        self.server.allow_reuse_address = True
        self.server.www_dir = config['www_dir']

    def start(self):
        self.logger.info('Starting server on {}:{}'.format(self.server.server_name, self.server.server_port))
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info('Server stopping')
