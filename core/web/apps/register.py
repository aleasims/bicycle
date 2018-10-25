from urllib import parse
from core.database.db_client import DBClient


def activate(args):
    response = b'HTTP/1.1 406\r\n'
    try:
        query = parse.parse_qs(args['input'].decode('utf-8'))
    except KeyError:
        return

    name = query['name'][0]
    passwd = query['passwd_hash'][0]

    cli = DBClient('/tmp/bc_ipc')
    if cli.create_new_user(name, passwd):
        response = b'HTTP/1.1 204\r\n'

    return response
