from urllib import parse
from core.database.db_client import DBClient
from core.database import db_proto


def activate(args):
    response = b'HTTP/1.1 406\r\n'
    try:
        query = parse.parse_qs(args['input'].decode('utf-8'))
    except KeyError:
        return

    name = query['name'][0]
    passwd = query['passwd_hash'][0]

    client = DBClient('/tmp/bc_ipc')
    request = db_proto.Request(method='NEWUSR', params={'name': name,
                                                        'passwd': passwd})
    if client.send(request).code == db_proto.DBRecpCode.OK:
        response = b'HTTP/1.1 201\r\n'

    return response
