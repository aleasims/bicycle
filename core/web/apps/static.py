import sys
import os
import urllib
from core.web.routes import routes


def activate(args):
    url = urllib.parse.urlparse(args['path'])
    query = urllib.parse.parse_qs(url[4])
    page_path = query['file'][0].lstrip('/')
    local_path = sys.path[0] + '/www/' + page_path
    if not os.path.exists(local_path):
        return b'HTTP/1.1 404'
    try:
        f = open(local_path)
        buf = f.read()
    except Exception as e:
        return b'HTTP/1.1 404'

    response = 'HTTP/1.1 200 OK'

    content_type = 'text/plain'
    if local_path.endswith('.html'):
        content_type = 'text/html'
    elif local_path.endswith('.js'):
        content_type = 'application/javascript'

    response = '\r\n'.join([response, 'Content-type: ' + content_type])
    response = '\r\n'.join([response, 'Content-length: {}'.format(len(buf))])
    response = '\r\n'.join([response, ''])
    response = '\r\n'.join([response, buf])
    return bytes(response, 'utf-8')