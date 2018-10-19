from urllib import parse
from enum import Enum


class DBRespCode(Enum):
    OK = 0
    FAIL = 1


class ParseError(Exception):
    def __repr__(self):
        return str(self.__class__.__name__ ) + 'Cannot parse request'


def parse_rq(request_bytes):
    request_string = request_bytes.decode('utf-8').rstrip('\n')
    splited = request_string.split(' ', 1)
    method_name = splited[0]
    params_string = ''
    if len(splited) > 1:
        params_string = splited[1]
    request = {}
    request['method'] = method_name
    request['params'] = parse.parse_qs(params_string)
    return request


def pack_rp(response_dir):
    if 'code' not in response_dir:
        return b'FAIL\n'
    code = response_dir['code'].name + '\n'

    data = ''
    if 'data' not in response_dir:
        return b'FAIL\n'
    for item in response_dir['data']:
        data += str(item)
        data += '\n'

    return bytes(code + data, 'utf-8')
