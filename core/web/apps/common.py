from http.cookies import BaseCookie
import datetime
from time import mktime
from wsgiref.handlers import format_date_time


def extract_ssid(args):
    cookie_str = args['headers'].get('Cookie')
    cookie = BaseCookie(cookie_str)
    ssid = cookie.get('SSID', None)
    return ssid


def get_expires_time(expires_time):
    now = datetime.datetime.now() + datetime.timedelta(0, expires_time)
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)
