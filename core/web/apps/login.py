import datetime
from time import mktime
from urllib import parse
from http.cookies import BaseCookie
from wsgiref.handlers import format_date_time
from core.database.db_client import DBClient, ClientError
from core.database import db_proto


DEFAULT_ENCODING = 'utf-8'
CHECKOUT_TIME = 600
db_cli = DBClient('/tmp/bc_ipc')


def activate(args):
    path = args.get('path')
    if not path:
        return
    path = parse.urlparse(path)

    # Check if is already logged and has a valid SSID
    if path.params == 'checkssid':
        return checkssid(args)

    # Handling log out requests
    if path.params == 'logout':
        return logout(args)

    # Handling log in requests
    # Get provided input data from request
    try:
        query = parse.parse_qs(args.get('input', '').decode(DEFAULT_ENCODING))
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


def logout(args):
    ssid = extract_ssid(args)
    if ssid:
        off_user = db_proto.Request(method='USROFF', params={'ssid': ssid.value})
        if db_cli.send(off_user) == db_proto.DBRespCode.OK:
            return bytes('HTTP/1.1 200\r\n' +
                         'X-Auth-status: OUT\r\n',
                         DEFAULT_ENCODING)
        else:
            return bytes('HTTP/1.1 200\r\n' +
                         'X-Auth-status: Logging out failed\r\n\r\n',
                         DEFAULT_ENCODING)


def authorize(name, passwd, client_ip):
    # Identification
    ident = db_proto.Request(method='CHECKUSR', params={'name': name})
    if db_cli.send(ident).code != db_proto.DBRespCode.OK:
        return bytes('HTTP/1.1 200\r\n' +
                     'X-Auth-status: Identification failed\r\n\r\n',
                     DEFAULT_ENCODING)

    # Authentication
    auth = db_proto.Request(method='CHECKPWD', params={'name': name,
                                                       'passwd': passwd})
    if db_cli.send(auth).code != db_proto.DBRespCode.OK:
        return bytes('HTTP/1.1 200\r\n' +
                     'X-Auth-status: Authentication failed\r\n\r\n',
                     DEFAULT_ENCODING)

    # Change user status to `online`
    mkonline = db_proto.Request(method='USRON', params={'name': name, 'client_ip': client_ip})
    db_response = db_cli.send(mkonline)
    if db_response.code == db_proto.DBRespCode.OK:
        ssid = db_response.data[0]
        return bytes('HTTP/1.1 200\r\n' +
                     'X-Auth-status: OK\r\n' +
                     'Set-Cookie: SSID={}; Max-Age={}; HttpOnly\r\n'.format(ssid, CHECKOUT_TIME),
                     DEFAULT_ENCODING)
    else:
        return bytes('HTTP/1.1 200\r\n' +
                     'X-Auth-status: Status failed\r\n',
                     DEFAULT_ENCODING)


def checkssid(args):
    ssid = extract_ssid(args)
    if ssid:
        cookiecheck = db_proto.Request(method='CHECKSSID',
                                       params={'ssid': ssid.value,
                                               'client_ip': args['client'][0]})
        response = db_cli.send(cookiecheck)
        if response.code == db_proto.DBRespCode.OK:
            return bytes('HTTP/1.1 200\r\n' +
                         'X-SSID-approvement: OK\r\n' +
                         'Set-Cookie: SSID={}; Max-Age={}\r\n'.format(
                            ssid, CHECKOUT_TIME) +
                         'Set-Cookie: nickname={}; Max-Age={}\r\n\r\n'.format(
                            response.data[0], CHECKOUT_TIME),
                         DEFAULT_ENCODING)
        else:
            return bytes('HTTP/1.1 200\r\n' +
                         'X-SSID-approvement: Invalid\r\n\r\n',
                         DEFAULT_ENCODING)
    return bytes('HTTP/1.1 200\r\n' +
                 'X-SSID-approvement: Not Found\r\n\r\n',
                 DEFAULT_ENCODING)


def extract_ssid(args):
    cookie_str = args.get('headers', {}).get('Cookie')
    cookie = BaseCookie(cookie_str)
    ssid = cookie.get('SSID', None)
    return ssid

def get_expires_time(expires_time):
    now = datetime.datetime.now() + datetime.timedelta(0, expires_time)
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)