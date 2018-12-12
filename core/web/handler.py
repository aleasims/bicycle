import os
import time
import sys
import importlib
import traceback
import urllib.parse
import email.utils
from http import HTTPStatus
from http.cookies import BaseCookie
from http.server import SimpleHTTPRequestHandler
from core.web import session

DEFAULT_ENCODING = 'utf-8'


class WebHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    SESS_EXP_TIME = 0
    SESS_KEY = 'bi_ssid'

    def authorize(self):
        self.authorized = False
        cookies = BaseCookie(self.headers['cookie'])
        ssid = cookies.get(self.SESS_KEY)
        if ssid is not None:
            uid = session.valid(ssid)
            if uid is not None:
                self.authorized = True

    def do_GET(self):
        self.authorize()
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_POST(self):
        raise Exception("POST NOT SUPPORTED")
        if self.headers['Content-length'] is None:
            self.send_response(HTTPStatus.LENGTH_REQUIRED)
            self.send_header('Connection', 'close')
            self.end_headers()
            return
        self.input = self.rfile.read(
            int(self.headers['Content-length'])).decode(DEFAULT_ENCODING)
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def version_string(self):
        return 'Bicycle/' + self.server.version

    def log_request(self, code='-', size='-'):
        message = '{}:{} - {} {} - {}'.format(
            *self.client_address, self.command, self.path, code)
        self.log_message(message)

    def log_error(self, form, *args):
        return
        message = '{}'.format(form % args)
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
            cache_time = email.utils.parsedate(self.headers['If-Modified-Since'])
            if cache_time and mtime <= time.mktime(cache_time):
                self.send_response(HTTPStatus.NOT_MODIFIED)
                self.end_headers()
                return
            self.send_response(HTTPStatus.OK)
            self.send_header('Set-Cookie', 'bi_ssid=123; Max-Age: 10')
            self.send_header('Content-type', self.guess_type(path))
            self.send_header('Content-Length', str(os.fstat(f.fileno())[6]))
            self.send_header('Last-Modified', self.date_time_string(mtime))
            self.end_headers()
            return f
        except Exception:
            f.close()
            raise

    def send_head(self):
        os.chdir(self.server.www_dir)
        path = self.translate_path(self.path)
        app_path = os.path.join(self.server.www_dir, 'app')
        if path.startswith(app_path):
            return self.send_app_head(path.replace(app_path, ''))
        # Static content:
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            for index in 'index.html', 'index.htm':
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
                else:
                    self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
                    return
        return self.send_file_head(path)

    def prepare_args(self, path):
        return {'app': path.lstrip('/'),
                'params': urllib.parse.urlsplit(self.path).query,
                'headers': self.headers,
                'client': self.client_address,
                'input': getattr(self, 'input', None)}

    def send_app_head(self, path):
        args = self.prepare_args(path)
        app = None
        try:
            app = importlib.import_module('core.web.apps.' + args['app'])
            if not hasattr(app, 'activate'):
                raise ImportError
        except ImportError:
            self.send_error(HTTPStatus.NOT_IMPLEMENTED)
            return

        response = {}
        try:
            response = app.activate(args)
        except Exception as e:
            traceback.print_exc()
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if not response or response.get('code') is None:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.send_response(response.get('code'))
        for hdr in response.get('headers', []):
            self.send_header(hdr[0], hdr[1])
        self.end_headers()
        return response.get('data')
