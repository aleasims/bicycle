from core.web import db


def create(name, passwd):
    if db.DBClient.send('GETIDBYNAME', {'name': name}).code.name == 'OK':
        return 'NAME_TAKEN',
    else:
        resp = db.DBClient.send('CREATEUSR', {'name': name, 'passwd': passwd})
        if resp.code.name == 'OK':
            return 'SUCCESSFUL', resp.data['uid']
        else:
            return 'FAILED',

def identify(name):
    resp = db.DBClient.send('GETIDBYNAME', {'name': name})
    if resp.code.name != 'OK':
        return None
    else:
        return resp.data['uid']

def authenticate(uid, passwd):
    return db.DBClient.send('CHECKPWD',
        {'uid': uid, 'passwd': passwd}).code.name == 'OK'
