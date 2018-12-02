from core.web.apps.common import DBClient


def identify(name):
    resp = DBClient.send('GETIDBYNAME', {'name': name})
    if resp.code.name != 'OK':
        return None
    else:
        return resp.data['uid']

def authenticate(uid, passwd):
    return DBClient.send('CHECKPWD',
        {'uid': uid, 'passwd': passwd}).code.name == 'OK'
