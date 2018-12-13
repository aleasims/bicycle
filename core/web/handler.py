import os
import time
import sys
import bs4
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
    SESS_EXP_TIME = 600
    SESS_KEY = 'bi_ssid'

    def check_session(self):
        self.user_id = None
        self.user_ssid = None
        ssid_cookie = BaseCookie(
            self.headers['cookie']).get(self.SESS_KEY)
        if ssid_cookie is not None:
            self.user_ssid = ssid_cookie.value
            self.user_id = session.valid(self.user_ssid)
            self.logger.debug('Session validated')

    def do_GET(self):
        self.check_session()
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_HEAD(self):
        self.check_session()
        self.send_head()

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

    def send_head(self):
        os.chdir(self.server.www_dir)
        path = self.translate_path(self.path)
        app_path = os.path.join(self.server.www_dir, 'app')
        if path.startswith(app_path):
            return self.send_app_head(path.replace(app_path, ''))
        # Static content:
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            index = os.path.join(path, 'index.html')
            if not os.path.exists(index):
                self.send_error(HTTPStatus.NOT_FOUND, 'File not found')
                return
        self.send_response(HTTPStatus.OK)
        return self.send_file_head(index)

    def send_file_head(self, path):
        f = None
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.CONFLICT, 'Cannot read file')
        try:
            ctype = self.guess_type(path)
            #soup = bs4.BeautifulSoup(model, 'html.parser')
            #print(soup)
            if self.user_ssid is not None:
                self.send_header('Set-Cookie', '{}={}; Max-Age: {}'.format(
                    self.SESS_KEY, self.user_ssid, self.SESS_EXP_TIME))
            self.send_header('Content-type', ctype)
            self.send_header('Content-Length', str(os.fstat(f.fileno())[6]))
            self.end_headers()
            return f
        except Exception as e:
            self.logger.error(e)
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)

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

    def prepare_args(self, path):
        return {'app': path.lstrip('/'),
                'user_id': self.user_id,
                'params': urllib.parse.urlsplit(self.path).query,
                'headers': self.headers,
                'client': self.client_address,
                'input': getattr(self, 'input', None)}
