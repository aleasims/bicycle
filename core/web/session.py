from core.web import db


def valid(ssid):
    dbresp = db.DBClient.send('GETSESS', {'ssid': ssid})
    if dbresp.code.name == 'FAIL':
        return
    return dbresp.data.get('uid')


def update(ssid):
    return db.DBClient.send('UPDSESS',
        {'ssid': ssid}).code.name == 'OK'


def create(uid, ip):
    dbresp = db.DBClient.send('CREATESESS',
        {'uid': uid, 'client_ip': ip})
    if dbresp.code.name == 'OK':
        return dbresp.data['ssid']
    else:
        return None


def drop(ssid):
    return db.DBClient.send('DROPSESS',
        {'ssid': ssid}).code.name == 'OK'
