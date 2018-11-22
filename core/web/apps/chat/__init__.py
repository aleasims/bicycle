import sys
import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web.apps.common import extract_ssid, valid_session
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
        return response


def makeactive(args):
    response = {
        'code': HTTPStatus.OK,
        'headers': [('Content-type', 'application/json')]
    }
    data = {'activation': False}

    ssid = extract_ssid(args)
    uid = valid_session(cli, ssid, ip=args['client'][0])
    if uid is not None:
        mk_active = db_proto.Request(method='MKUSRACTIVE',
                                     params={'uid': uid})
        data = {'activation': cli.send(mk_active).code == DBRespCode.OK}
    else:
        data['reason'] = 'Invalid session'

    data = bytes(json.dumps(data), 'utf-8')
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(data)
    return response


def getonlineusr(args):
    response = {
        'code': HTTPStatus.OK,
        'headers': [('Content-type', 'application/json')]
    }
    cli.send(db_proto.Request(method='REVISACTIVE'))
    resp = cli.send(db_proto.Request(method='LISTACTIVE'))
    ssid = extract_ssid(args)
    if ssid:
        cookiecheck = db_proto.Request(method='CHECKSSID',
                                       params={'ssid': ssid.value,
                                               'client_ip': args['client'][0]})
        if cli.send(cookiecheck).code == db_proto.DBRespCode.OK:
            mk_active = db_proto.Request(method='MKUSRACTIVE',
                                         params={'ssid': ssid.value})
            data = bytes(json.dumps(
                {'Activation': cli.send(mk_active).code == DBRespCode.OK}),
                'utf-8')
    if resp.code != db_proto.DBRespCode.OK:
        return response
    data = bytes(json.dumps(resp.data), 'utf-8')
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(data)
    return response
