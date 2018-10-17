def activate(args):
    response = b'HTTP/1.1 204\r\n'
    try:
        query = urllib.parse.parse_qs(args['input'])
    except KeyError:
        return

    name = query['nickname']

    return response