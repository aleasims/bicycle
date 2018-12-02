from core.web.apps.common import DBClient


def valid(ssid, ip):
    dbresp = DBClient.send('GETSESS', {'ssid': ssid})
    if dbresp.code.name == 'FAIL':
        return False
    sess = dbresp.data
    return sess['clientIP'] == ip


def update(ssid):
    return DBClient.send('UPDSESS',
        {'ssid': ssid}).code.name == 'OK'


def create(uid, ip):
    dbresp = DBClient.send('CREATESESS',
        {'uid': uid, 'client_ip': ip})
    if dbresp.code.name == 'OK':
        return dbresp.data['ssid']
    else:
        return None


def drop(ssid):
    return DBClient.send('DROPSESS',
        {'ssid': ssid}).code.name == 'OK'
