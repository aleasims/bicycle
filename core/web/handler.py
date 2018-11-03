from http.server import BaseHTTPRequestHandler
from core.web import app_handler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.base_handle()

    def do_POST(self):
        if self.headers['Content-length'] is None:
            self.wfile.write(b'HTTP/1.1 411')
        self.input = self.rfile.read(int(self.headers['Content-length']))
        self.base_handle()

    def base_handle(self):
        args = self.prepare_args()
        response = app_handler.LaunchApp(args)
        self.wfile.write(response)
        self.log(response)

    def prepare_args(self):
        args = {'path': self.path}
        if getattr(self, 'input', None) is not None:
            args['input'] = self.input 
        return args

    def log(self, response):
        if hasattr(self, 'logger'):
            code = response.decode('utf-8').split('\r\n', 1)[0].split(' ', 1)[1]
            log_message = '{}:{} - {} {} - {}'.format(*self.client_address,
                                                    self.command,
                                                    self.path,
                                                    code)
            self.logger.info(log_message)