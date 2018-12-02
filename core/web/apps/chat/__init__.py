import sys
import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web.apps.common import DBClient, extract_ssid, get_expires_time


THIS_APP = sys.modules[__name__]
DEFAULT_ACTION = 'makeactive'
ENC = 'utf-8'


def activate(args):
    params = parse.parse_qs(args['params'])
    action = params.get('action', [None]).pop()
    if action is None:
        action = DEFAULT_ACTION

    response = {
        'headers': [('Connection', 'close')]
    }
    try:
        action = getattr(THIS_APP, action)
    except AttributeError:
        response['code'] = HTTPStatus.NOT_IMPLEMENTED
    else:
        response['code'] = HTTPStatus.OK

        data = action(args, response)
        if data is not None:
            data = json.dumps(data)
            response['headers'].append(('Content-type', 'application/json;charset={}'.format(ENC)))
            response['headers'].append(('Content-length', str(len(data))))
            response['data'] = BytesIO(bytes(data, ENC))
    return response


def getonlineusr(args, response):
    data = {'online': []}
    dbresp = DBClient.send('ONLINEUIDS')
    if dbresp.code.name != 'OK':
        return data
    dbresp = DBClient.send('GETNAMESBYIDS', {'uids': dbresp.data['uids']})
    if dbresp.code.name != 'OK':
        return data
    data['online'] = dbresp.data
    return data
