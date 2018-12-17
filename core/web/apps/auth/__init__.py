import sys
import json
from io import BytesIO
from urllib import parse
from http import HTTPStatus
from core.web import session
from core.web import user


CHECKOUT_TIME = 300
ENC = 'utf-8'
DEFAULT_ACTION = 'login'
THIS_APP = sys.modules[__name__]


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
        data = action(args, response)
        if data:
            response['code'] = HTTPStatus.OK
            data = json.dumps(data)
            response['headers'].append(('Content-type', 'application/json;charset={}'.format(ENC)))
            response['headers'].append(('Content-length', str(len(data))))
            response['data'] = BytesIO(bytes(data, ENC))
    finally:
        return response


def login(args, response):
    # Handling login requests
    #
    # Reqeust example:
    # GET /app/auth?name=Sasha&pwd=sdjcn23jnd322jdjkn
    # or (same):
    # GET /app/auth?action=login&name=Sasha&pwd=sdjcn23jnd322jdjkn

    # Get nickname and pwd
    params = parse.parse_qs(args.get('params', ''))
    name = params.get('name', [None])[-1]
    passwd = params.get('pwd', [None])[-1]
    if name is None or passwd is None:
        response['code'] = HTTPStatus.BAD_REQUEST
        return {}

    uid = user.identify(name)
    if uid is None:
        return {'status': 'FAILED', 'msg': 'Identification failed'}

    if not user.authenticate(uid, passwd):
        return {'status': 'FAILED', 'msg': 'Authentication failed'}

    ssid = session.create(uid)
    if ssid is None:
        return {'status': 'FAILED', 'msg': 'Session not created'}

    response['headers'].append(('Set-Cookie', '{}={}; Mag-Age={}'.format(
                                session.SESS_KEY, ssid, session.SESS_EXP_TIME)))
    return {'status': 'SUCCESSFUL'}


def logout(args, response):
    # Handling log out requests
    #
    # Request example:
    # GET /app/auth?action=logout

    user = args['user']
    if user is not None:
        if not session.drop(user['ssid']):
            return {'status': 'FAILED'}
    return {'status': 'SUCCESSFUL'}
