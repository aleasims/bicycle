from http.server import BaseHTTPRequestHandler
from core.web.routes import routes
from http import HTTPStatus
from core.web import app_handler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        app = self.validate(self.path)
        if app is not None:
            response = app_handler.LaunchApp(app, {'path': self.path})
            self.wfile.write(response)

        else:
            print('Not found: ' + self.path)
            self.wfile.write(app_handler.LaunchApp('static', {'path': '/error'}))

    def validate(self, path):
        app = None
        if path in routes['static']['html'] \
            or path in routes['static']['js']:
            app = 'static'
        elif path in routes['apps']:
            app = routes['apps'][path]
        return app
