import sys
import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web.common import extract_ssid
from core.database import db_proto
from core.database.db_proto import DBRespCode
from core.database.db_client import DBClient


app = sys.modules[__name__]
DEFAULT_ACTION = 'makeactive'
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
        response = action(args)
        response['headers'].append(('Connection', 'close'))


def makeactive(args):
    response = {
        'code': HTTPStatus.OK,
        'headers': []
    }
    mk_active = db_proto.Request(method='MKUSRCHAT',
                                 params={'ssid': extract_ssid(args)})
    resp = cli.send(mk_active)
    if resp.code != DBRespCode.OK:
        data = 
    return response


def getonlineusr(args):
    response = {
        'code': HTTPStatus.OK,
        'headers': [('Content-type', 'application/json')]
    }
    online_usr = db_proto.Request(method='LISTACTIVE')
    resp = cli.send(online_usr)
    if resp.code != db_proto.DBRespCode.OK:
        return response
    data = bytes(json.dumps(resp.data), 'utf-8')
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(data)
    return response
