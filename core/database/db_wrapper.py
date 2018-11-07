import os
import uuid
import time
import traceback
from tinydb import TinyDB, Query
from tinydb.operations import delete
from core.database import db_proto
from core.database.db_proto import DBRespCode
from core.database.cache import Cacher


class DBWrapper:
    def __init__(self, logger, storage_path):
        self.logger = logger
        self.storage_path = storage_path
        self.db = TinyDB(os.path.join(storage_path, 'data.json'))
        self.users = self.db.table('users')
        self.cache = Cacher(tables={'online': ('nickname', 'SSID', 'lastAct')})
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

    def CHECKSSID(self, params):
        ssid = params['ssid'][-1]
        # user = self.cache.online.get(SSID=ssid)
        # if len(user) > 0 and user[0].SSID == ssid:
        user = self.users.get(Query()['SSID'] == ssid)
        if user:
            return db_proto.Response(code=DBRespCode.OK, data=[user['name']])
        return db_proto.Response(code=DBRespCode.FAIL)

    def USRON(self, params):
        name = params['name'][-1]
        ssid = uuid.uuid4().hex
        self.users.update({'logged': True,
                           'SSID': ssid,
                           'lastAct': time.time()}, Query()['name'] == name)
        # self.cache.online.add(SSID=ssid, nickname=name, lastAct=round(time.time()))
        return db_proto.Response(code=DBRespCode.OK, data=[ssid])

    def USROFF(self, params):
        ssid = params['ssid'][-1]
        self.users.update({'logged': False}, Query()['SSID'] == ssid)
        self.users.update(delete('lastAct'), Query()['SSID'] == ssid)
        self.users.update(delete('SSID'), Query()['SSID'] == ssid)
        # self.cache.online.remove(SSID=)
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