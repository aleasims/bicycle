import tinydb
import os
from core.database.db_proto import DBRespCode


class DBWrapper:
    def __init__(self, storage_path):
        self.storage_path = storage_path
        self.db = tinydb.TinyDB(os.path.join(storage_path, 'data.json'))
        self.users = self.db.table('users')

    def NEWUSR(self, params):
        response = {'data': []}
        name = params['name'][-1]
        User = tinydb.Query()
        if self.users.contains(User['name'] == name):
            response['code'] = DBRespCode.FAIL
        else:
            self.users.insert({'name': name, 'level': 0})
            response['code'] = DBRespCode.OK
        return response

    def LISTUSR(self, params):
        response = {'code': DBRespCode.OK, 'data': []}
        for user in self.users:
            response['data'].append(user['name'])
        return response

    def DELALLUSR(self, params):
        self.users.purge()
        return {'code': DBRespCode.OK, 'data': []}