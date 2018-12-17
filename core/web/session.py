from core.web import db


SESS_EXP_TIME = 600
SESS_KEY = 'bi_ssid'


def validate(ssid):
    dbresp = db.DBClient.send('GETSESS', {'ssid': ssid})
    if dbresp.code.name == 'FAIL':
        return
    uid = dbresp.data.get('uid')
    dbresp = db.DBClient.send('GETUSRBYID', {'uid': uid})
    if dbresp.code.name == 'FAIL':
        return
    user = dbresp.data
    if user is not None:
        user['ssid'] = ssid
    return user


def update(ssid):
    return db.DBClient.send('UPDSESS',
        {'ssid': ssid}).code.name == 'OK'


def create(uid):
    dbresp = db.DBClient.send('CREATESESS',
        {'uid': uid})
    if dbresp.code.name == 'OK':
        return dbresp.data['ssid']
    else:
        return None


def drop(ssid):
    return db.DBClient.send('DROPSESS',
        {'ssid': ssid}).code.name == 'OK'
