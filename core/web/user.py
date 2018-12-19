from core.web import db
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTPServer = None
HOMEADDR = None
WEBHOST = None

VERIFY_MAIL_SUBJ = 'Bicycle account verification'
VERIFY_MAIL_BODY = '''
Here is you link to verify account:

%(host)s/app/register?action=verify&id=%(uid)s&token=%(token)s

'''


def register_verificator(host, mailhost, port, address, password):
    global SMTPServer, HOMEADDR, WEBHOST
    SMTPServer = smtplib.SMTP(mailhost, 587)
    SMTPServer.ehlo()
    SMTPServer.starttls()
    SMTPServer.login(address, password)
    HOMEADDR = address
    WEBHOST = host


def create(name, passwd, email):
    if db.DBClient.send('GETIDBYNAME', {'name': name}).code.name == 'OK':
        return 'NAME_TAKEN',
    else:
        resp = db.DBClient.send('CREATEUSR', {'name': name, 'passwd': passwd, 'email': email})
        if resp.code.name == 'OK':
            return 'SUCCESSFUL', resp.data['uid'], resp.data['verify_token']
        else:
            return 'FAILED',

def identify(name):
    resp = db.DBClient.send('GETIDBYNAME', {'name': name})
    if resp.code.name != 'OK':
        return None
    else:
        return resp.data['uid']

def authenticate(uid, passwd):
    return db.DBClient.send('CHECKPWD',
        {'uid': uid, 'passwd': passwd}).code.name == 'OK'

def send_token(uid, email, token):
    msg = MIMEMultipart()
    msg['From'] = HOMEADDR
    msg['To'] = email
    msg['Subject'] = VERIFY_MAIL_SUBJ
    body = MIMEText(VERIFY_MAIL_BODY % {'host': WEBHOST, 'uid': uid, 'token': token}, 'plain')
    msg.attach(body)
    SMTPServer.sendmail(HOMEADDR, email, msg.as_string())

def verify(uid, token):
    dbresp = db.DBClient.send('GETUSRBYID', {'uid': int(uid)})
    if dbresp.code.name != 'OK':
        return None
    if token == dbresp.data['verify_token']:
        dbresp = db.DBClient.send('USRVERIFIED', {'uid': int(uid)})
        return dbresp.code.name == 'OK'

def verified(uid):
    dbresp = db.DBClient.send('GETUSRBYID', {'uid': int(uid)})
    if dbresp.code.name == 'OK':
        return dbresp.data['verified']
