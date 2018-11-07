import sys
import os
from urllib import parse
from http.cookies import BaseCookie
from core.web.routes import routes
from core.database.db_client import DBClient
from core.database import db_proto


DEFAULT_ENCODING = 'utf-8'


def activate(args):
    path = args.get('path')
    if not path:
        return

    query = parse.parse_qs(parse.urlparse(path)[4])
    page_path = query['file'][0].lstrip('/')
    local_path = sys.path[0] + '/www/' + page_path
    # print('Local path: {}'.format(local_path))

    if not os.path.exists(local_path):
        return bytes('HTTP/1.1 404\r\n',DEFAULT_ENCODING)
    try:
        f = open(local_path)
        data = f.read()
    except Exception as e:
        return bytes('HTTP/1.1 500\r\n', DEFAULT_ENCODING)

    response = 'HTTP/1.1 200 OK'
    response = '\r\n'.join([response, 'Content-type: {}'.format(guess_type(local_path))])
    response = '\r\n'.join([response, 'Content-length: {}'.format(len(data))])
    response = '\r\n'.join([response, ''])
    response = '\r\n'.join([response, data])
    return bytes(response, DEFAULT_ENCODING)


def guess_type(local_path):
    content_type = 'text/plain'
    if local_path.endswith('.html'):
        content_type = 'text/html'
    elif local_path.endswith('.js'):
        content_type = 'application/javascript'
    return content_type