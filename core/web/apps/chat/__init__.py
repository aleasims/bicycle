import sys
import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.database import db_proto
from core.database.db_client import DBClient


app = sys.modules[__name__]
DEFAULT_ACTION = 'login'
cli = DBClient('/tmp/bc_ipc')


def activate(args):
    params = parse.parse_qs(args.get('params', ''))
    action = params.get('action')
    if not action:
        action = [DEFAULT_ACTION]

    try:
        action = getattr(app, action[-1])
    except AttributeError:
        return {'code': HTTPStatus.NOT_IMPLEMENTED}
    else:
        return action(args)


def getonlineusr(args):
    response = {
        'code': HTTPStatus.OK,
        'headers': [('Content-type', 'application/json')]
    }
    online_usr = db_proto.Request(method='LISTONUSR')
    resp = cli.send(online_usr)
    if resp.code != db_proto.DBRespCode.OK:
        return response
    data = bytes(json.dumps(resp.data), 'utf-8')
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(data)
    return response
