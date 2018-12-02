'''
Discribes protocol for communicating with context database.
Performs serialization job and parse
'''
# TODO: validate request method names (capital latin letters)
# TODO: check existance of `SEP` in data
# TODO: think of another `EOS`
from urllib import parse
from enum import Enum
from core import common
import json


EOM = '\r\n'
ENCODING = 'utf-8'
DELIMITER = bytes(EOM, ENCODING)
SEP = '|'
SPACE = ' '
MAX_REQUEST_LEN = 1024
MAX_REPR_LEN = 50


class DBRespCode(Enum):
    OK = 0
    FAIL = 1


class Error(Exception):
    pass


class ProtoMessage:
    def __init__(self):
        raise Error('Unspecified ProtoMessage')

    def parse(self, _bytes):
        _str = self.decode(_bytes)
        identificator, additions = self.defragment(_str)
        return identificator, additions

    def decode(self, _bytes):
        if not (isinstance(_bytes, bytes) or isinstance(_bytes, bytearray)):
            raise Error('Invalid argument, byte-like expected')
        try:
            _str = _bytes.decode(ENCODING)
        except UnicodeDecodeError:
            raise Error('Failed to decode bytes')
        return _str

    def defragment(self, string):
        if EOM not in string:
            raise Error('No EOM in the end')
        stripped = string.split(EOM, 1)[0]
        splitted = stripped.split(SPACE, 1)
        if len(splitted) < 2:
            splitted.append('')
        return splitted

    def pack_fragments(self, fragments):
        tmp = fragments[0]
        if fragments[1]:
            tmp = SPACE.join([tmp, fragments[1]])
        tmp += EOM
        return tmp


class Request(ProtoMessage):
    def __init__(self, _bytes=None, method=None, params={}):
        if _bytes is not None:
            self.method, self.params = self.parse(_bytes)
            self.bytes = self.pack(self.method, self.params)
        elif method is not None:
            self.bytes = self.pack(method, params)
            self.method, self.params = self.parse(self.bytes)
        else:
            super().__init__()

    def __repr__(self):
        return '<{}.{} method={} params={} bytes={}>'.format(
            self.__class__.__bases__[0].__name__,
            type(self).__name__, self.method,
            common.format(self.params, MAX_REPR_LEN),
            common.format(self.bytes, MAX_REPR_LEN))

    def parse(self, _bytes):
        method, params_string = super().parse(_bytes)
        method = self.validate_method(method)
        params = self.parse_params(params_string)
        return method, params

    def pack(self, method, params):
        method = self.validate_method(method)
        try:
            params_string = json.dumps(params)
        except TypeError:
            raise Error('Params are not serializable')
        _str = self.pack_fragments([method, params_string])
        return bytes(_str, ENCODING)

    def validate_method(self, method):
        if type(method) != str or not method or not method.isalpha():
            raise Error('Invalid method name')
        if not method.isupper():
            method = method.upper()
        return method

    def parse_params(self, params_string):
        try:
            params = json.loads(params_string)
        except json.JSONDecodeError:
            raise Error('Data decoding failed')
        return params

    def decode(self, _bytes):
        _str = super().decode(_bytes)
        if len(_str) > MAX_REQUEST_LEN:
            raise Error('Request too long')
        return _str


class Response(ProtoMessage):
    '''
    `data` - must be json-serializable
    '''
    def __init__(self, _bytes=None, code=None, data={}):
        if _bytes is not None:
            self.code, self.data = self.parse(_bytes)
            self.bytes = _bytes
        elif code is not None:
            self.bytes = self.pack(code, data)
            self.code = code
            self.data = data
        else:
            super().__init__()

    def __repr__(self):
        return '<{}.{} code={} data={} bytes={}>'.format(
            self.__class__.__bases__[0].__name__,
            type(self).__name__, self.code.name,
            common.format(self.data, MAX_REPR_LEN),
            common.format(self.bytes, MAX_REPR_LEN))

    def parse(self, _bytes):
        code_string, data_string = super().parse(_bytes)
        if code_string not in DBRespCode.__members__:
            raise Error('Invalid code')
        code = getattr(DBRespCode, code_string)
        try:
            data = json.loads(data_string)
        except json.JSONDecodeError:
            raise Error('Data decoding failed')
        return code, data

    def pack(self, code, data):
        if type(code) != DBRespCode:
            raise Error('Invalid code')
        try:
            data_str = json.dumps(data)
        except TypeError:
            raise Error('Data is not serializable')
        _str = self.pack_fragments([code.name, data_str])
        return bytes(_str, ENCODING)
