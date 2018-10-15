import importlib
import urllib
from core.web.routes import routes


def LaunchApp(args):
    ERROR_RESPONSE = b'HTTP/1.1 500\r\n\r\n'

    try:
        path = args['path']
    except KeyError:
        return

    path = urllib.parse.urlparse(path)[2]

    if path not in routes:
        args['path'] = ''.join(['/static?file=', path])
        response = LaunchApp(args)
    elif routes[path].startswith('/'):
        args['path'] = routes[path]
        response = LaunchApp(args)
    else:
        appname = routes[path]
        app = importlib.import_module('core.web.apps.' + appname)
        response = app.activate(args)

    return response
