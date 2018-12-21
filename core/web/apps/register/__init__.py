import json
from io import BytesIO
from http import HTTPStatus
from urllib import parse
from core.web import user


VERIFICATION_DONE = '''
<html>
<body>
<h1>Account verified</h1>
<h3>Redirecting to homepage...</h3>
<script>setTimeout(() => {window.location.replace("/")}, 3000)</script>
</body>
</html>
'''

VERIFICATION_FAILED = '''
<html>
<body>
<h1>Account verification failed!</h1>
<h3>Something went wrong, try again later or create new account</h3>
</body>
</html>
'''


def activate(args):
    # Handle register request
    # Accepts new user name, pwd hash and email
    #
    # Request example:
    # GET /app/register?name=Sasha&pwd=as322mdj93dk&email=sasha@example.com

    params = parse.parse_qs(args['params'])

    action = params.get('action', [None]).pop()
    if action is not None:
        if action == 'verify':
            return verify(args)

    name = params.get('name', [None])[-1]
    passwd = params.get('pwd', [None])[-1]
    email = params.get('email', [None])[-1]

    if name is None or passwd is None or email is None:
        return {'code': HTTPStatus.BAD_REQUEST,
                'headers': [('Connection', 'close')]}

    response = {
        'code': HTTPStatus.OK,
        'headers': [('Connection', 'close'),
                    ('Content-type', 'application/json')]
    }
    result = user.create(name, passwd, email)
    data = {
        'status': result[0]
    }
    if len(result) > 1 and result[0] == 'SUCCESSFUL':
        uid = result[1]
        token = result[2]
        user.send_token(uid, email, token)
        data['uid'] = uid

    data = json.dumps(data)
    response['headers'].append(('Content-length', str(len(data))))
    response['data'] = BytesIO(bytes(data, 'utf-8'))
    return response

def verify(args):
    params = parse.parse_qs(args['params'])
    token = params.get('token', [None])[-1]
    uid = params.get('id', [None])[-1]
    if token is None or uid is None:
        return {'code': HTTPStatus.BAD_REQUEST,
                'headers': [('Connection', 'close')]}

    if user.verify(uid, token):
        return {'code': HTTPStatus.OK,
                'headers': [
                    ('Connection', 'close'),
                    ('Content-type', 'text/html; charset=utf-8'),
                    ('Content-length', str(len(VERIFICATION_DONE)))],
                'data': BytesIO(VERIFICATION_DONE.encode('utf-8'))}

    return {'code': HTTPStatus.OK,
            'headers': [
                ('Connection', 'close'),
                ('Content-type', 'text/html; charset=utf-8'),
                ('Content-length', str(len(VERIFICATION_FAILED)))],
            'data': BytesIO(VERIFICATION_FAILED.encode('utf-8'))
            }
