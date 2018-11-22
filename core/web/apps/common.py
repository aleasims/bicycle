from http.cookies import BaseCookie
import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from core.database import db_proto


def extract_ssid(args):
    cookie_str = args['headers'].get('Cookie')
    cookie = BaseCookie(cookie_str)
    ssid = cookie.get('SSID', None)
    return ssid


def valid_session(client, ssid, ip):
    if ssid and client.send(
        db_proto.Request(
            method='CHECKSSID',
            params={'ssid': ssid.value,
                    'client_ip': ip})).code == db_proto.DBRespCode.OK:
        uid = client.send(
            db_proto.Request(
                method='GETUID',
                params={'ssid': ssid.value})).data
        if uid:
            return uid[0]


def get_expires_time(expires_time):
    now = datetime.datetime.now() + datetime.timedelta(0, expires_time)
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)
