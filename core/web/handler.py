import os
import time
import sys
import importlib
import urllib.parse
import email.utils
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler


class WebHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = 'BicycleWEB/0.1b'
    www_dir = '/home/alea/bicycle/www'
    app_path = os.path.join(www_dir, 'app')

    def do_POST(self):
        if self.headers['Content-length'] is None:
            self.wfile.write(b'HTTP/1.1 411')
            return
        self.input = self.rfile.read(int(self.headers['Content-length']))
        self.send_head()
        self.close_connection = True

    def version_string(self):
        return self.server_version

    def log_request(self, code='-', size='-'):
        message = '{}:{} - {} {} - {}'.format(
            *self.client_address, self.command, self.path, code)
        self.log_message(message)

    def log_error(self, format, *args):
        return
        message = '{}:{} - {}'.format(*self.client_address, format % args)
        self.log_message(message)

    def log_message(self, message):
        if hasattr(self, 'logger'):
            self.logger.info(message)
        else:
            sys.stdout.write(message + '\n')

    def send_moved_to(self, new_path):
        self.send_response(HTTPStatus.MOVED_PERMANENTLY)
        parts = urllib.parse.urlsplit(self.path)
        new_parts = (parts[0], parts[1], new_path,
                     parts[3], parts[4])
        new_url = urllib.parse.urlunsplit(new_parts)
        self.send_header('Location', new_url)
        self.end_headers()

    def send_file_head(self, path):
        f = None
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
            return
        try:
            mtime = os.path.getmtime(path) + time.timezone
            if 'If-Modified-Since' in self.headers:
                cache_time = time.mktime(
                    email.utils.parsedate(self.headers['If-Modified-Since']))
                if mtime <= cache_time:
                    self.send_response(HTTPStatus.NOT_MODIFIED)
                    self.end_headers()
                    return
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', self.guess_type(path))
            self.send_header('Content-Length', str(os.fstat(f.fileno())[6]))
            self.send_header('Last-Modified', self.date_time_string(mtime))
            self.end_headers()
            return f
        except Exception:
            f.close()
            raise

    def send_head(self):
        self.close_connection = True
        os.chdir(self.www_dir)
        path = self.translate_path(self.path)
        if path.startswith(self.app_path):
            self.local_path = path
            self.serve_app()
            return
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                self.send_moved_to(parts.path + '/')
                return
            for index in 'index.html', 'index.htm':
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
                    return
        return self.send_file_head(path)

    def prepare_args(self):
        parts = urllib.parse.urlsplit(self.path)
        args = {'app': self.local_path.lstrip(self.app_path),
                'params': parts.query,
                'fragment': parts.fragment,
                'headers': self.headers,
                'client': self.client_address}
        if getattr(self, 'input', None) is not None:
            args['input'] = self.input
        return args

    def serve_app(self):
        args = self.prepare_args()
        app = None
        try:
            app = importlib.import_module('core.web.apps.' + args['app'])
        except ImportError:
            self.wfile.write(b'HTTP/1.1 400\r\n\r\n')
            self.log_request('400')
            return
        response = app.activate(args)
        if not response:
            response = b'HTTP/1.1 500\r\n\r\n'
        self.wfile.write(response)
        self.log_request(response.decode('utf-8').rstrip('\r\n').split(' ', 2)[1])
