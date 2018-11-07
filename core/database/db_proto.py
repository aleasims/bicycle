# TODO: validate request method names (capital latin letters)
# TODO: check existance of `SEP` in data
from urllib import parse
from enum import Enum


EOS = '\n' # still not the best one
ENCODING = 'utf-8'
DELIMITER = bytes(EOS, ENCODING)
SEP = '|'
SPACE = ' '


class DBRespCode(Enum):
    OK = 0
    FAIL = 1


class Error(Exception):
    pass


class ProtoMessage:
    def __init__(self, _bytes=None):
        if _bytes:
            self._bytes = _bytes
            self._parse()
            return
        raise Error('Unspecified ProtoMessage')

    @property
    def bytes(self):
        if not hasattr(self, '_bytes'):
            self._pack()
        return self._bytes

    def _pack_fragments(self, fragments):
        if fragments[1]:
            self._bytes = bytes(SPACE.join(fragments) + EOS, ENCODING)
        else:
            self._bytes = bytes(fragments[0] + EOS, ENCODING)

    def _defragment(self):
        try:
            decoded = self.bytes.decode(ENCODING)
        except UnicodeDecodeError:
            raise Error('Failed to decode bytes')
        if EOS not in decoded:
            raise Error('No EOS in the end')
        stripped = decoded.split(EOS, 1)[0]
        splitted = stripped.split(SPACE, 1)
        if len(splitted) < 2:
            splitted.append('')
        return splitted

    def _pack(self):
        raise NotImplementedError

    def _parse(self):
        raise NotImplementedError


class Request(ProtoMessage):
    def __init__(self, _bytes=None, method='', params={}):
        if method:
            if type(method) != str or not method.isalpha():
                raise Error('Invalid method name')
            self.method = method
            if type(params) != dict:
                raise Error('Params should be a dict instance')
            self.params = params
            return
        super().__init__(_bytes)

    def _parse(self):
        self.method, params_string = self._defragment()
        self.params = parse.parse_qs(params_string)

    def _pack(self):
        param_list = []
        for key, value in self.params.items():
            param_list.append('='.join([key, value]))
        fragments = [self.method, '&'.join(param_list)]
        self._pack_fragments(fragments)


class Response(ProtoMessage):
    def __init__(self, _bytes=None, code=None, data=[]):
        if code:
            if not type(code) == DBRespCode:
                raise Error('Unsupported code')
            self.code = code
            if not type(data) == list:
                raise Error('Data should be a list instance')
            self.data = data
            return
        super().__init__(_bytes)

    def _parse(self):
        code_string, data_string = self._defragment()
        if code_string not in DBRespCode.__members__:
            raise Error('Unsupported code')
        self.code = getattr(DBRespCode, code_string)
        self.data = data_string.split(SEP)

    def _pack(self):
        fragments = [self.code.name, SEP.join(self.data)]
        self._pack_fragments(fragments)
