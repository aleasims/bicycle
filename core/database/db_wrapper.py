import os
import uuid
import time
import traceback
from tinydb import TinyDB, Query
from tinydb.operations import delete
from core.database import db_proto
from core.database.db_proto import DBRespCode


class DBWrapper:
    '''
    User and Message database API class
    In fact - wrapper from TinyDB, transformint it for context database
    '''
    def __init__(self, logger, storage_path, exp_time):
        self.logger = logger
        self.EXPIRE_TIME = exp_time
        self.storage_path = storage_path
        self.db = TinyDB(os.path.join(storage_path, 'data.json'))
        self.users = self.db.table('users')
        # add IP

    def __log_err(self, err):
        self.logger.error(err)
        traceback.print_exc()

    def perform(self, request):
        perform = getattr(self, request.method, None)
        if not perform:
            raise Exception('Unsupported request method')
        try:
            return perform(request.params)
        except Exception as err:
            self.__log_err(err)
            return db_proto.Response(code=DBRespCode.FAIL)

    # Wrapping functions:
    # - named with capital latin letters only
    # - accepts `params` argument - dict-like object

    def CHECKSSID(self, params):
        client_ip = params['client_ip'][-1]
        ssid = params['ssid'][-1]
        user = self.users.get(Query()['SSID'] == ssid)
        if user and user['client_ip'] == client_ip and \
                (int(time.time()) - user['lastAct'] < self.EXPIRE_TIME):
            return db_proto.Response(code=DBRespCode.OK, data=[user['name']])
        return db_proto.Response(code=DBRespCode.FAIL)

    def USRON(self, params):
        name = params['name'][-1]
        client_ip = params['client_ip'][-1]
        ssid = uuid.uuid4().hex
        self.users.update({'logged': True,
                           'client_ip': client_ip,
                           'SSID': ssid,
                           'lastAct': int(time.time())}, Query()['name'] == name)
        return db_proto.Response(code=DBRespCode.OK, data=[ssid])

    def USROFF(self, params):
        ssid = params['ssid'][-1]
        self.users.update({'logged': False}, Query()['SSID'] == ssid)
        self.users.update(delete('lastAct'), Query()['SSID'] == ssid)
        self.users.update(delete('client_ip'), Query()['SSID'] == ssid)
        self.users.update(delete('SSID'), Query()['SSID'] == ssid)
        return db_proto.Response(code=DBRespCode.OK)

    def NEWUSR(self, params):
        name = params['name'][-1]
        passwd = params['passwd'][-1]
        if self.users.contains(Query()['name'] == name):
            return db_proto.Response(code=DBRespCode.FAIL)

        self.users.insert({'name': name,
                           'passwd': passwd,
                           'registerDate': time.ctime(),
                           'logged': False})
        return db_proto.Response(code=DBRespCode.OK)

    def CHECKUSR(self, params):
        name = params['name'][-1]
        if self.users.contains(Query()['name'] == name):
            return db_proto.Response(code=DBRespCode.OK)
        return db_proto.Response(code=DBRespCode.FAIL)

    def CHECKPWD(self, params):
        name = params['name'][-1]
        pwd = params['passwd'][-1]
        user = self.users.get(Query()['name'] == name)
        if pwd == user['passwd']:
            return db_proto.Response(code=DBRespCode.OK)
        return db_proto.Response(code=DBRespCode.FAIL)

    def LISTUSR(self, params):
        data = []
        for user in self.users:
            data.append(user['name'])
        return db_proto.Response(code=DBRespCode.OK, data=data)

    def DELALLUSR(self, params):
        raise Exception('DELALLUSR tried')
        try:
            self.users.purge()
            return db_proto.Response(code=DBRespCode.OK)
        except Exception:
            return db_proto.Response(code=DBRespCode.FAIL)
