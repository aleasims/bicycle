import sys
from core.web.routes import routes


def activate(args):
    path = ''
    content_type = ''
    if args['path'] in routes['static']['html']:
        path = 'html/' + routes['static']['html'][args['path']]
        content_type = 'text/html'
    elif args['path'] in routes['static']['js']:
        path = 'js/' + routes['static']['js'][args['path']]
        content_type = 'application/javascript'
    local_path = sys.path[0] + '/www/' + path
    f = open(local_path)
    buf = f.read()
    response = 'HTTP/1.1 200 OK'
    response = '\r\n'.join([response, 'Content-type: ' + content_type])
    response = '\r\n'.join([response, 'Content-length: {}'.format(len(buf))])
    response = '\r\n'.join([response, ''])
    response = '\r\n'.join([response, buf])
    return response