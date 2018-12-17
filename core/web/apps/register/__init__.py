import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web import user


def activate(args):
    # Handle register request
    # Accepts new user name and pwd hash
    #
    # Request example:
    # GET /app/register?name=Sasha&pwd=as322mdj93dk

    params = parse.parse_qs(args['params'])
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
    result = user.create(name, passwd)
    print(result)
    data = {
        'status': result[0]
    }
    if len(result) > 1 and result[0] == 'SUCCESSFUL':
        data['uid'] = result[1]

    data = json.dumps(data)
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(bytes(data, 'utf-8'))
    return response
