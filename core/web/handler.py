import os
import io
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
from core.web import view


DEFAULT_ENCODING = 'utf-8'
__version__ = '0.3'


class WebHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    server_version = 'Bicycle/' + __version__

    @property
    def error_message_format(self):
        return view.error_message(getattr(self, 'user', None))

    def do_HEAD(self):
        self.check_session()
        self.send_head()

    def do_GET(self):
        self.check_session()
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def do_POST(self):
        self.check_session()
        self.handle_input()
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()

    def check_session(self):
        self.user = None
        cookie = self.headers['cookie']
        if cookie is None:
            return
        ssid_cookie = BaseCookie(cookie).get(session.SESS_KEY)
        if ssid_cookie is None:
            return
        ssid = ssid_cookie.value
        user_data = session.validate(ssid)
        if user_data is None:
            ssid = None
        self.user = user_data

    def handle_input(self):
        if self.headers['Content-length'] is None:
            self.send_error(HTTPStatus.LENGTH_REQUIRED)
            return
        self.input = self.rfile.read(
            int(self.headers['Content-length'])).decode(DEFAULT_ENCODING)

    def version_string(self):
        return self.server_version

    def log_request(self, code='-', size='-'):
        message = '{}:{} - {} {} - {}'.format(
            *self.client_address, self.command, self.path, code)
        self.log_message(message)

    def log_message(self, message):
        if hasattr(self, 'logger'):
            self.logger.info(message)
        else:
            sys.stdout.write(message + '\n')

    def log_error(self, string, code, message):
        pass

    def send_head(self):
        self.close_connection = True
        os.chdir(self.server.www_dir)
        path = self.translate_path(self.path)
        app_path = os.path.join(self.server.www_dir, 'app')
        if path.startswith(app_path):
            return self.app_response(path.replace(app_path, ''))
        if os.path.isdir(path):  # Page requested
            content = os.path.join(path, 'content.html')
            if not os.path.exists(content):
                self.send_error(HTTPStatus.NOT_FOUND, 'This page does not exist')
                return
            return self.send_personal_head(content)
        else:
            if not os.path.exists(path):
                self.send_error(HTTPStatus.NOT_FOUND, 'This page does not exist')
                return
            return self.send_static_head(path)

    def send_personal_head(self, content):
        page = view.fill(content, self.user)
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html; charset={}'.format(DEFAULT_ENCODING))
        self.send_header('Content-Length', str(len(page)))
        if self.user is not None:
            self.send_header('Set-Cookie', '{}={}; Max-Age: {}'.format(
                session.SESS_KEY, self.user['ssid'], session.SESS_EXP_TIME))
        self.end_headers()
        return io.BytesIO(page.encode(DEFAULT_ENCODING))

    def send_static_head(self, path):
        f = open(path, 'rb')
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', self.guess_type(path))
        self.send_header('Content-Length', str(os.fstat(f.fileno())[6]) + 
            '; charset={}'.format(DEFAULT_ENCODING))
        if self.user is not None:
            self.send_header('Set-Cookie', '{}={}; Max-Age: {}'.format(
                session.SESS_KEY, self.user['ssid'], session.SESS_EXP_TIME))
        self.end_headers()
        return f

    def app_response(self, path):
        args = self.prepare_args(path)
        app = None
        try:
            app = importlib.import_module('core.web.apps.' + args['app'])
            if not hasattr(app, 'activate'):
                raise ImportError('No activate function in app')
        except ImportError as e:
            self.logger.debug(e)
            self.send_error(HTTPStatus.NOT_IMPLEMENTED)
            return

        response = {}
        try:
            response = app.activate(args)
        except Exception as e:
            self.logger.debug(e)
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
        return {
            'app': path.lstrip('/'),
            'params': urllib.parse.urlsplit(self.path).query,
            'headers': self.headers,
            'user': self.user,
            'client': self.client_address,
            'input': getattr(self, 'input', None)
        }
