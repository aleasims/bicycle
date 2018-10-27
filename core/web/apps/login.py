from urllib import parse
from core.database.db_client import DBClient
from core.database import db_proto


def activate(args):
    response = b'HTTP/1.1 400\r\n'
    try:
        query = parse.parse_qs(args['input'].decode('utf-8'))
    except KeyError:
        return

    name = query['name'][0]
    passwd = query['passwd_hash'][0]

    client = DBClient('/tmp/bc_ipc')
    request = db_proto.Request(method='CHECKUSR', params={'name': name})
    response = client.send(request)
    if response.code != db_proto.DBRespCode.OK:
        return b'HTTP/1.1 404\r\n'

    request = db_proto.Request(method='CHECKPWD', params={'name': name,
                                                          'passwd': passwd})
    response = client.send(request)
    if response.code != db_proto.DBRespCode.OK:
        return b'HTTP/1.1 401\r\n'

    return b'HTTP/1.1 200\r\nSet-cookie: SSID=100000\r\n'
