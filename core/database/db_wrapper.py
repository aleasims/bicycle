import tinydb
import os
from core.database.db_proto import DBRespCode


class DBWrapper:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        self.db = tinydb.TinyDB(os.path.join(storage_path, 'data.json'))
        self.users = self.db.table('users')

    def NEWUSR(self, params):
        name = params['name'][-1]
        passwd = params['passwd'][-1]
        User = tinydb.Query()
        if self.users.contains(User['name'] == name):
            code = DBRespCode.FAIL
        else:
            self.users.insert({'name': name, 'passwd': passwd})
            code = DBRespCode.OK
        return db_proto.Response(code=code)

    def CHECKUSR(self, params):
        name = params['name'][-1]
        User = tinydb.Query()
        if self.users.contains(User['name'] == name):
            code = DBRespCode.OK
        else:
            self.users.insert({'name': name, 'passwd': passwd})
            code = DBRespCode.FAIL
        return db_proto.Response(code=code)

    def CHECKPWD(self, params):
        name = params['name'][-1]
        pwd = params['passwd'][-1]
        User = tinydb.Query()
        usr = self.users.search(User.name == name)[-1]
        if pwd == usr['passwd']:
            return db_proto.Response(code=db_proto.DBRespCode.OK)
        return db_proto.Response(code=db_proto.DBRespCode.FAIL)

    def LISTUSR(self, params):
        data = []
        for user in self.users:
            data.append(user['name'])
        return db_proto.Response(code=DBRespCode.OK, data=data)

    def DELALLUSR(self, params):
        try:
            self.users.purge()
            return db_proto.Response(code=DBRespCode.OK)
        except Exception:
            return db_proto.Response(code=DBRespCode.FAIL)