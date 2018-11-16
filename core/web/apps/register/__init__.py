from http import HTTPStatus
from urllib import parse
from core.database.db_client import DBClient
from core.database import db_proto


client = DBClient('/tmp/bc_ipc')


def activate(args):
    # Handle register request
    # Accepts new user name and pwd hash
    #
    # Request example:
    # GET /app/register?name=Sasha&pwd=as322mdj93dk

    params = parse.parse_qs(args.get('params', ''))
    name = params.get('name', [None])[-1]
    passwd = params.get('pwd', [None])[-1]
    if name is None or passwd is None:
        return {'code': HTTPStatus.BAD_REQUEST}

    response = {
        'code': HTTPStatus.OK,
        'headers': []
    }
    request = db_proto.Request(method='NEWUSR',
                               params={'name': name,
                                       'passwd': passwd})
    if client.send(request).code == db_proto.DBRespCode.OK:
        response['headers'].append(('X-Reg-status', 'OK'))
    else:
        response['headers'].append(('X-Reg-status', 'FAIL'))
    return response
