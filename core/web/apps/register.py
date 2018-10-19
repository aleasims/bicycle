from urllib import parse


def activate(args):
    response = b'HTTP/1.1 204\r\n'
    try:
        query = parse.parse_qs(args['input'].decode('utf-8'))
    except KeyError:
        return

    name = query['name']

    return response