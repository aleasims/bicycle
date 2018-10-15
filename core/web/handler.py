from http.server import BaseHTTPRequestHandler
from core.web import app_handler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        args = self.prepare_args()
        response = app_handler.LaunchApp(args)
        self.wfile.write(response)
        self.log(response)

    def do_POST(self):
        pass

    def prepare_args(self):
        return {'path': self.path}

    def log(self, response):
        code = response.decode('utf-8').split('\r\n', 1)[0].split(' ', 1)[1]
        log_message = '{}:{} - {} {} - {}'.format(*self.client_address,
                                                  self.command,
                                                  self.path,
                                                  code)
        self.logger.info(log_message)