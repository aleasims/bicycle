import sys
import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web import db
from core.web import session
from core.web import longpoll


THIS_APP = sys.modules[__name__]
ENC = 'utf-8'
MAX_TIMEOUT = 120
MIN_TIMEOUT = 1


def activate(args):
    params = parse.parse_qs(args['params'])
    action = params.get('action', ['']).pop()

    response = {
        'headers': [('Connection', 'close')]
    }
    if args['user'] is None:
        response['code'] = HTTPStatus.FORBIDDEN
        return response
    try:
        action = getattr(THIS_APP, action)
    except AttributeError:
        response['code'] = HTTPStatus.NOT_IMPLEMENTED
    else:
        response['code'] = HTTPStatus.OK

        data = action(args, response)
        if data is not None:
            data = json.dumps(data)
            response['headers'].append(('Content-type', 'application/json;charset={}'.format(ENC)))
            response['headers'].append(('Content-length', str(len(data))))
            response['data'] = BytesIO(bytes(data, ENC))
    return response


def getonlineusr(args, response):
    data = {'online': []}
    dbresp = db.DBClient.send('ONLINEUIDS')
    if dbresp.code.name != 'OK':
        return data
    dbresp = db.DBClient.send('GETNAMESBYIDS', {'uids': dbresp.data['uids']})
    if dbresp.code.name != 'OK':
        return data
    data['online'] = [{'uid': usr[0], 'name': usr[1]} for usr in dbresp.data]
    return data


def accept(args, response):
    params = parse.parse_qs(args.get('params', ''))
    timeout = int(params.get('timeout', [MAX_TIMEOUT]).pop())
    timeout = timeout if timeout <= MAX_TIMEOUT else MAX_TIMEOUT
    timeout = timeout if timeout >= MIN_TIMEOUT else MIN_TIMEOUT

    user = args['user']
    uid = user['uid']
    def get_new_chnls():
        resp = db.DBClient.send('FINDCHNLBYTGT', {'uid': uid, 'status': 'REQ'})
        if resp.code.name == 'OK' and resp.data:
            return resp.data

    new_chnls = longpoll.wait(get_new_chnls,
                              test=lambda x: x is not None,
                              timeout=timeout,
                              default=[],
                              polling_time=1)
    data = {'accepted': new_chnls}
    return data


def request(args, response):
    params = parse.parse_qs(args.get('params', ''))
    timeout = int(params.get('timeout', [MAX_TIMEOUT]).pop())
    timeout = timeout if timeout <= MAX_TIMEOUT else MAX_TIMEOUT
    timeout = timeout if timeout >= MIN_TIMEOUT else MIN_TIMEOUT

    target_id = int(params['uid'].pop())
    user = args['user']
    dbresp = db.DBClient.send('CREATECHNL', {'initiator': user['uid'],
                                             'target': target_id,
                                             'status': 'REQ'})
    if dbresp.code.name == 'FAIL':
        return {'answer': 'error'}

    chid = dbresp.data['chid']
    def get_answer():
        dbresp = db.DBClient.send('GETCHNL', {'chid': chid})
        if dbresp.code.name == 'OK':
            return dbresp.data

    chnl = longpoll.wait(get_answer,
                         test=lambda x: x['status'] != 'REQ',
                         timeout=timeout,
                         default=None,
                         polling_time=1)

    if chnl is None:
        db.DBClient.send('DROPCHNL', {'chid': chid})
        return {'answer': 'timeout'}
    elif chnl['status'] == 'DIS':
        db.DBClient.send('DROPCHNL', {'chid': chid})
        return {'answer': 'dismissed'}
    elif chnl['status'] == 'ACC':
        db.DBClient.send('CHANGECHNLSTATUS', {'chid': chid, 'status': 'RUN'})
        return {'answer': 'accepted', 'channel': chnl}
    return {'answer': 'error'}


def dismiss(args, response):
    params = parse.parse_qs(args.get('params', ''))
    chid = params.get('chid', [None]).pop()
    if chid is None:
        response['code'] = HTTPStatus.BAD_REQUEST
        return
    dbresp = db.DBClient.send('CHANGECHNLSTATUS', {'chid': chid, 'status': 'DIS'})
    return {}


def prove(args, response):
    params = parse.parse_qs(args.get('params', ''))
    chid = params.get('chid', [None]).pop()
    if chid is None:
        response['code'] = HTTPStatus.BAD_REQUEST
        return
    dbresp = db.DBClient.send('CHANGECHNLSTATUS', {'chid': chid, 'status': 'ACC'})
    return {}
