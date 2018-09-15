from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from core.web.routes import routes
from core.web.static_handler import StaticHandler
from core.web.app_handler import AppHandler
from http import HTTPStatus
from http.server import HTTPServer

class WebServer(HTTPServer):
    # it's possible not use static variables for logger nad config by overriding Base_server.finish_request
    def __init__(self, config, logger):
        WebServer.config = config
        WebServer.logger = logger
        self.host = config["host"]
        self.port = config["port"]
        super().__init__((self.host, self.port), self.MasterHandler)

    def start(self):
        self.logger.info('Web server started')
        super().serve_forever()

    def finish_request(self, request, client_address):
        self.MasterHandler(request, client_address, self, self.config, self.logger)

    class MasterHandler(BaseHTTPRequestHandler):
        def __init__(self, request, client_address, server, config, logger):
            super().__init__(request, client_address, server)
            self.config, self.logger = config, logger

        def handle_one_request(self):
            super().handle_one_request()
            if (self.path in list(routes["apps"].keys())):
                if (WebServer.logger is not None):
                    WebServer.logger.info("Handle request by AppHandler")
                AppHandler(self.request, self.client_address, self.server)
            else:
                if (WebServer.logger is not None):
                    WebServer.logger.info("Handle request by StaticHandler")
                StaticHandler(self.request, self.client_address, self.server)
        
        def send_error(self, code, message=None, explain=None):
            if code==HTTPStatus.NOT_IMPLEMENTED:
                return
            else:
                super().send_error