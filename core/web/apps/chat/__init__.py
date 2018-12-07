import sys
import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web.apps.common import DBClient, extract_ssid, get_expires_time
from core.web.apps.auth import session
from core.web.apps.chat import longpoll


THIS_APP = sys.modules[__name__]
DEFAULT_ACTION = 'makeactive'
ENC = 'utf-8'
MAX_TIMEOUT = 120
MIN_TIMEOUT = 5


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
    data['online'] = [{'uid': usr[0], 'name': usr[1]} for usr in dbresp.data]
    return data

def accept(args, response):
    params = parse.parse_qs(args.get('params', ''))
    timeout = params.get('timeout', [MAX_TIMEOUT]).pop()
    timeout = timeout if timeout <= MAX_TIMEOUT else MAX_TIMEOUT
    timeout = timeout if timeout >= MIN_TIMEOUT else MIN_TIMEOUT

    ssid = extract_ssid(args)
    if ssid is not None and session.valid(ssid, args['client'][0]):
        uid = session.uid(ssid)

        def get_new_chnls():
            resp = DBClient.send('FINDCHNL', {'uid': uid, 'status': 'REQ'})
            if resp.code.name == 'OK' and resp.data:
                return resp.data

        new_chnls = longpoll.wait(get_new_chnls,
                                  test=lambda x: x is not None,
                                  timeout=timeout,
                                  default=[])
        data = {'accepted': new_chnls}
        return data
    else:
        response['code'] = HTTPStatus.FORBIDDEN
        return
