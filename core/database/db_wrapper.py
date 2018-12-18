import os
import uuid
import time
import traceback
from tinydb import TinyDB, Query
from tinydb.database import Document
from tinydb.operations import delete
from tinydb.storages import MemoryStorage
from core.database import db_proto
from core.database.db_proto import DBRespCode
from core.common import create_unique_token


SEED = 1000  # adding to used id to normalize it


class DBWrapper:
    '''
    User and Message database API class
    In fact - wrapper from TinyDB, transforming it for context database
    '''
    def __init__(self, logger, storage_path, exp_time):
        self.logger = logger
        self.SESS_EXP_TIME = exp_time
        self.ABANDON_TIME = 60

        self.db = TinyDB(os.path.join(storage_path, 'data.json'))
        self.users = self.db.table('users')
        self.private = self.db.table('private')

        self.tmp = TinyDB(os.path.join(storage_path, 'tmp.json'))
        self.sessions = self.tmp.table('sessions')
        self.channels = self.tmp.table('channels')

    def __log_err(self, err):
        self.logger.debug('Exception during performing DB operation: {}'.format(err))
        traceback.print_exc()

    def perform(self, request):
        perform = getattr(self, request.method, None)
        if not perform:
            return db_proto.Response(code=DBRespCode.FAIL,
                                     data={'msg': 'Unsupported method'})
        try:
            return perform(request.params)
        except Exception as err:
            traceback.print_exc()
            self.__log_err(err)
            return db_proto.Response(code=DBRespCode.FAIL)

    # Wrapping functions:
    # - named with capital latin letters only
    # - accepts only (!) `params` argument - dict-like object

# SESSIONS
    def CREATESESS(self, params):
        # Creates session for user
        # Returns generated ssid
        # Requires: `uid`
        #
        for i in range(0, 10):
            ssid = uuid.uuid4().hex
            SSIDs = [sess['ssid'] for sess in self.sessions.all()]
            if ssid not in SSIDs:
                break
        else:
            raise Exception('Number of attempts exceeded')
        self.sessions.upsert({'uid': params['uid'],
                              'ssid': ssid,
                              'lastUpd': int(time.time())},
                              Query()['uid'] == params['uid'])
        return db_proto.Response(code=DBRespCode.OK, data={'ssid': ssid})

    def GETSESS(self, params):
        # Returns session with provided ssid
        # Requires: `ssid`
        #
        sess = self.sessions.get(Query()['ssid'] == params['ssid'])
        if sess is None:
            return db_proto.Response(code=DBRespCode.FAIL)
        return db_proto.Response(code=DBRespCode.OK, data=sess)

    def UPDSESS(self, params):
        # Updates lastUpd timestamp
        # Requires: `ssid`
        #
        sess = self.sessions.get(Query()['ssid'] == params['ssid'])
        if sess is None:
            return db_proto.Response(code=DBRespCode.FAIL)
        self.sessions.update({'lastUpd': int(time.time())},
                             doc_ids=[sess.doc_id])
        return db_proto.Response(code=DBRespCode.OK)

    def DROPSESS(self, params):
        # Removes session with given ssid
        # Requires: `ssid`
        #
        ssid = params['ssid']
        sess = self.sessions.get(Query()['ssid'] == ssid)
        if sess is not None:
            self.sessions.remove(doc_ids=[sess.doc_id])
        return db_proto.Response(code=DBRespCode.OK)

    def ONLINEUIDS(self, params):
        # Returns list of uids of logged users
        # Requires: -
        #
        uids = [sess['uid'] for sess in self.sessions.all()]
        return db_proto.Response(code=DBRespCode.OK, data={'uids': uids})

# USER
    def CREATEUSR(self, params):
        # Create new user if possible
        # Returns uid of created user
        # Requires: `name`, `passwd`, `email`
        #
        if self.users.contains(Query()['name'] == params['name']):
            return db_proto.Response(code=DBRespCode.FAIL)  # Name must be unique
        doc_id = self.users.insert({'name': params['name'],
                                    'registerDate': time.ctime()})
        uid = SEED + doc_id
        self.users.update({'uid': uid}, doc_ids=[doc_id])
        self.private.insert({'uid': uid,
                             'passwd': params['passwd']})
        return db_proto.Response(code=DBRespCode.OK, data={'uid': uid})

    def GETUSRBYID(self, params):
        # Returns user info for given uid
        # Requires: `uid`
        #
        user = self.users.get(Query()['uid'] == params['uid'])
        if user is None:
            return db_proto.Response(code=DBRespCode.FAIL)
        return db_proto.Response(code=DBRespCode.OK, data=user)

    def GETNAMESBYIDS(self, params):
        # Return user names for given uids
        # Requires: `uids`
        #
        names = []
        for uid in params['uids']:
            usr = self.users.get(Query()['uid'] == uid)
            if usr is not None:
                names.append((uid, usr['name']))
        return db_proto.Response(code=DBRespCode.OK, data=names)

    def GETIDBYNAME(self, params):
        # Checks if user with provided name exists
        # Return uid if user found
        # Requires: `name`
        #
        user = self.users.get(Query()['name'] == params['name'])
        if user is not None:
            return db_proto.Response(code=DBRespCode.OK, data={'uid': user['uid']})
        return db_proto.Response(code=DBRespCode.FAIL)

    def CHECKPWD(self, params):
        # Checks if provided password is correct
        # Requires: `uid`, `passwd`
        #
        record = self.private.get(Query()['uid'] == params['uid'])
        if params['passwd'] == record['passwd']:
            return db_proto.Response(code=DBRespCode.OK)
        return db_proto.Response(code=DBRespCode.FAIL)

    def DELUSR(self, params):
        # Delets user, if passwd provided correctly
        # Requires: `uid`, `passwd`
        #
        record = self.private.get(Query()['uid'] == params['uid'])
        if params['passwd'] == record['passwd']:
            self.private.remove(doc_ids=[record.doc_id])
            self.users.remove(Query()['uid'] == [params['uid']])
            return db_proto.Response(code=DBRespCode.OK)
        return db_proto.Response(code=DBRespCode.FAIL)

# CHANNELS
    def CREATECHNL(self, params):
        target, initiator = params['target'], params['initiator']
        if target == initiator:
            return db_proto.Response(code=DBRespCode.FAIL,
                                     data={'msg': 'Users must be different'})
        users = []
        for uid in target, initiator:
            usr = self.users.get(Query()['uid'] == uid)
            if usr is None:
                return db_proto.Response(code=DBRespCode.FAIL,
                                         data={'msg': 'User not found'})
            users.append(usr)

        chid = create_unique_token([chnl['chid'] for chnl in self.channels.all()])

        self.channels.insert({'chid': chid,
                              'status': params['status'],
                              'target': users[0],
                              'initiator': users[1],
                              'buffer': {
                                    params['target']: [],
                                    params['initiator']: []}})
        return db_proto.Response(code=DBRespCode.OK, data={'chid': chid})

    def GETCHNL(self, params):
        chid = params['chid']
        chnl = self.channels.get(Query()['chid'] == chid)
        if chnl is None:
            return db_proto.Response(code=DBRespCode.FAIL,
                                     data={'msg': 'Channel not found'})
        return db_proto.Response(code=DBRespCode.OK, data=chnl)

    def CHANGECHNLSTATUS(self, params):
        chid = params['chid']
        new_status = params['status']
        if self.channels.get(Query()['chid'] == chid) is None:
            return db_proto.Response(code=DBRespCode.FAIL,
                                     data={'msg': 'Channel not found'})
        self.channels.update({'status': new_status},
                             Query()['chid'] == chid)
        return db_proto.Response(code=DBRespCode.OK)

    def FINDCHNLBYTGT(self, params):
        uid = params['uid']
        status = params.get('status')
        if status is not None:
            chnls = self.channels.search((Query()['target']['uid'] == uid) & (Query()['status'] == status))
        else:
            chnls = self.channels.search(Query()['target']['uid'] == uid)
        return db_proto.Response(code=DBRespCode.OK, data=chnls)

    def DROPCHNL(self, params):
        chid = params['chid']
        chnl = self.channels.get(Query()['chid'] == chid)
        if chnl is not None:
            self.channels.remove(doc_ids=[chnl.doc_id])
        return db_proto.Response(code=DBRespCode.OK)
