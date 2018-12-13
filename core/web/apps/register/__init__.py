import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web import db
from core.database import db_proto


def activate(args):
    # Handle register request
    # Accepts new user name and pwd hash
    #
    # Request example:
    # GET /app/register?name=Sasha&pwd=as322mdj93dk

    params = parse.parse_qs(args.get('params', ''))
    name = params.get('name', [None])[-1]
    passwd = params.get('pwd', [None])[-1]
    if name is None or passwd is None:
        return {'code': HTTPStatus.BAD_REQUEST,
                'headers': [('Connection', 'close')]}

    response = {
        'code': HTTPStatus.OK,
        'headers': [('Connection', 'close'),
                    ('Content-type', 'application/json')]
    }
    data = {}

    if db.DBClient.send('GETIDBYNAME', {'name': name}).code == db_proto.DBRespCode.OK:
        data = {'status': 'NAME_TAKEN'}
    else:
        resp = db.DBClient.send('CREATEUSR', {'name': name, 'passwd': passwd})
        if resp.code == db_proto.DBRespCode.OK:
            data = {'status': 'SUCCESSFUL',
                    'uid': resp.data['uid']}
        else:
            data = {'status': 'FAILED'}

    data = json.dumps(data)
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(bytes(data, 'utf-8'))
    return response
