from core.web import db


def identify(name):
    resp = db.DBClient.send('GETIDBYNAME', {'name': name})
    if resp.code.name != 'OK':
        return None
    else:
        return resp.data['uid']

def authenticate(uid, passwd):
    return db.DBClient.send('CHECKPWD',
        {'uid': uid, 'passwd': passwd}).code.name == 'OK'
