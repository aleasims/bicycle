import sys
from urllib import parse
from http import HTTPStatus
from core.web.apps.common import extract_ssid
from core.database.db_client import DBClient
from core.database import db_proto


CHECKOUT_TIME = 600
DEFAULT_ACTION = 'login'
db_cli = DBClient('/tmp/bc_ipc')
app = sys.modules[__name__]


def activate(args):
    params = parse.parse_qs(args['params'])
    action = params.get('action')
    if not action:
        action = [DEFAULT_ACTION]

    try:
        action = getattr(app, action[-1])
    except AttributeError:
        return {'code': HTTPStatus.NOT_IMPLEMENTED}
    else:
        return action(args)


def login(args):
    # Handling login requests
    #
    # Reqeust example:
    # GET /app/auth?name=Sasha&pwd=sdjcn23jnd322jdjkn
    # or (same):
    # GET /app/auth?action=authorize&name=Sasha&pwd=sdjcn23jnd322jdjkn

    # Get nickname and pwd
    params = parse.parse_qs(args.get('params', ''))
    name = params.get('name', [None])[-1]
    passwd = params.get('pwd', [None])[-1]
    if name is None or passwd is None:
        return {'code': HTTPStatus.BAD_REQUEST}

    response = {
        'code': HTTPStatus.OK,
        'headers': []
    }

    # Identification
    identify = db_proto.Request(method='CHECKUSR',
                                params={'name': name})
    if db_cli.send(identify).code != db_proto.DBRespCode.OK:
        response['headers'].append(('X-Auth-status', 'Identification failed'))
        return response

    # Authentication
    auth = db_proto.Request(method='CHECKPWD',
                            params={'name': name,
                                    'passwd': passwd})
    if db_cli.send(auth).code != db_proto.DBRespCode.OK:
        response['headers'].append(('X-Auth-status', 'Authentication failed'))
        return response

    # Change user status to `online`
    mkonline = db_proto.Request(method='USRON',
                                params={'name': name,
                                        'client_ip': args['client'][0]})
    db_response = db_cli.send(mkonline)
    if db_response.code == db_proto.DBRespCode.OK:
        ssid = db_response.data[0]
        response['headers'].append(('X-Auth-status', 'OK'))
        response['headers'].append(('Set-Cookie', 'SSID={}; Max-Age={}; HttpOnly'.format(
            ssid, CHECKOUT_TIME)))
    else:
        response['headers'].append(('X-Auth-status', 'Status failed'))
    return response


def checkssid(args):
    # Check if client has valid SSID
    #
    # Request example:
    # GET /app/auth?action=checkssid

    response = {
        'code': HTTPStatus.OK,
        'headers': []
    }

    ssid = extract_ssid(args)
    if ssid:
        cookiecheck = db_proto.Request(method='CHECKSSID',
                                       params={'ssid': ssid.value,
                                               'client_ip': args['client'][0]})
        resp = db_cli.send(cookiecheck)
        if resp.code == db_proto.DBRespCode.OK:
            response['headers'].append(('X-SSID-approvement', 'OK'))
            response['headers'].append(('Set-Cookie', 'SSID={}; Max-Age={}'.format(
                ssid.value, CHECKOUT_TIME)))
            response['headers'].append(('Set-Cookie', 'nickname={}; Max-Age={}'.format(
                resp.data[0], CHECKOUT_TIME)))
        else:
            response['headers'].append(('X-SSID-approvement', 'Invalid'))
    else:
        response['headers'].append(('X-SSID-approvement', 'Not Found'))
    return response


def logout(args):
    # Handling log out requests
    #
    # Request example:
    # GET /app/auth?action=logout

    ssid = extract_ssid(args)
    if ssid:
        off_user = db_proto.Request(method='USROFF', params={'ssid': ssid.value})
        if db_cli.send(off_user) == db_proto.DBRespCode.OK:
            return {'code': HTTPStatus.OK,
                    'headers': [('X-Auth-status', 'OUT')]}
        else:
            return {'code': HTTPStatus.OK,
                    'headers': [('X-Auth-status', 'Logging out failed')]}
    return {'code': HTTPStatus.OK,
            'headers': [('X-Auth-status', 'OUT')]}
