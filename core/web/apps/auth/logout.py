from core.web.apps.common import extract_ssid


def activate(args):
    ssid = extract_ssid(args)
    if ssid:
        off_user = db_proto.Request(method='USROFF', params={'ssid': ssid.value})
        if db_cli.send(off_user) == db_proto.DBRespCode.OK:
            return {'code': HTTPStatus.OK,
                    'headers': {
                        'X-Auth-status': 'OUT'}}
        else:
            return {'code': HTTPStatus.OK,
                    'headers': {
                        'X-Auth-status': 'Logging out failed'}}