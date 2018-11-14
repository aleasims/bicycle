from urllib import parse
from http import HTTPStatus
from core.web.apps.common import extract_ssid
from core.database.db_client import DBClient, ClientError
from core.database import db_proto


CHECKOUT_TIME = 600
db_cli = DBClient('/tmp/bc_ipc')


def activate(args):
    # Handling log in requests
    # Get provided input data from request
    query = {}
    try:
        query = parse.parse_qs(args.get('input', ''))
    except UnicodeDecodeError:
        return

    # Get nickname and pwd from input data
    name = query.get('name', [None])[-1]
    passwd = query.get('passwd_hash', [None])[-1]
    if not name or not passwd:
        return bytes('HTTP/1.1 400\r\n\r\n', DEFAULT_ENCODING)

    # Try to authorize user
    try:
        return authorize(name, passwd, args['client'][0])
    except (ClientError, db_proto.Error) as e:
        print(e)

    return bytes('HTTP/1.1 500\r\n\r\n', DEFAULT_ENCODING)


def authorize(name, passwd, client_ip):
    # Identification
    ident = db_proto.Request(method='CHECKUSR', params={'name': name})
    response = {'code': HTTPStatus.OK}
    if db_cli.send(ident).code != db_proto.DBRespCode.OK:
        response['headers'] = {'X-Auth-status': 'Identification failed'}
        return response

    # Authentication
    auth = db_proto.Request(method='CHECKPWD', params={'name': name,
                                                       'passwd': passwd})
    if db_cli.send(auth).code != db_proto.DBRespCode.OK:
        response['headers'] = {'X-Auth-status': 'Authentication failed'}
        return response

    # Change user status to `online`
    mkonline = db_proto.Request(method='USRON', params={'name': name, 'client_ip': client_ip})
    db_response = db_cli.send(mkonline)
    if db_response.code == db_proto.DBRespCode.OK:
        ssid = db_response.data[0]
        response['headers'] = {'X-Auth-status': 'OK',
                               'Set-Cookie': 'SSID={}; Max-Age={}; HttpOnly'.
                               format(ssid, CHECKOUT_TIME)}
    else:
        response['headers'] = {'X-Auth-status': 'Status failed'}
    return response


def checkssid(args):
    ssid = extract_ssid(args)
    response = {'code': HTTPStatus.OK}
    if ssid:
        cookiecheck = db_proto.Request(method='CHECKSSID',
                                       params={'ssid': ssid.value,
                                               'client_ip': args['client'][0]})
        resp = db_cli.send(cookiecheck)
        if resp.code == db_proto.DBRespCode.OK:
            response['headers'] = {'X-SSID-approvement': 'OK',
                                   'Set-Cookie': 'SSID={}; Max-Age={}'.format(ssid, CHECKOUT_TIME),
                                   'Set-Cookie': 'nickname={}; Max-Age={}'.format(resp.data[0], CHECKOUT_TIME)}
        else:
            response['headers'] = {'X-SSID-approvement': 'Invalid'}
    else:
        response['headers'] = {'X-SSID-approvement': 'Not Found'}
    return response






