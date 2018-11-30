import os
import sys
import unittest

sys.path.insert(0, os.path.join(sys.path[0], '..'))
from core.database.db_client import Client
from core.database.db_proto import Request, Response, Error, DBRespCode


C = Client('/tmp/bc_ipc')


class TestDBMethods(unittest.TestCase):
    def test_CREATEUSR(self):
        self.assertEqual(C.send('CREATEUSR', {}).code,
                         DBRespCode.FAIL)
        self.assertEqual(C.send('CREATEUSR', {'name': 'Dima', 'passwd': '1234567'}).code,
                         DBRespCode.OK)
        self.assertEqual(C.send('CREATEUSR', {'name': 'Dima', 'passwd': '1234567'}).code,
                         DBRespCode.FAIL)

    def test_GETUSRBYID(self):
        resp = C.send('CREATEUSR', {'name': 'skndclksn', 'passwd': '1234567'})
        self.assertEqual(C.send('GETUSRBYID', {'uid': resp.data['uid']}).code,
                         DBRespCode.OK)

    def test_GETNAMESBYIDS(self):
        self.assertEqual(C.send('GETNAMESBYIDS', {'uids': [1, 2, 3]}).code,
                         DBRespCode.OK)

    def test_GETIDBYNAME(self):
        resp = C.send('CREATEUSR', {'name': 'aaaaaaaaaa', 'passwd': '1234567'})
        self.assertEqual(C.send('GETIDBYNAME', {'name': 'aaaaaaaaaa'}).data['uid'],
                         resp.data['uid'])

    def test_CHECKPWD(self):
        resp = C.send('CREATEUSR', {'name': 'bbbbbbb', 'passwd': '1234567'})
        self.assertEqual(C.send('CHECKPWD', {'uid': resp.data['uid'], 'passwd': '1234567'}).code,
                         DBRespCode.OK)

    def test_DELUSR(self):
        resp = C.send('CREATEUSR', {'name': 'ccccccccc', 'passwd': '1234567'})
        self.assertEqual(C.send('DELUSR', {'uid': resp.data['uid'], 'passwd': '1234567'}).code,
                         DBRespCode.OK)

    def test_CREATESESS(self):
        resp = C.send('CREATEUSR', {'name': '12332ksl', 'passwd': '1234567'})
        self.assertEqual(C.send('CREATESESS', {'uid': resp.data['uid'], 'client_ip': '123.456.789.000'}).code,
                         DBRespCode.OK)

    def test_ONLINEUIDS(self):
        self.assertEqual(C.send('ONLINEUIDS', {}).code,
                         DBRespCode.OK)

    def test_GETSESS(self):
        resp = C.send('CREATEUSR', {'name': '121dsdskdkl', 'passwd': '1234567'})
        resp = C.send('CREATESESS', {'uid': resp.data['uid'], 'client_ip': '123.456.789.000'})
        self.assertEqual(C.send('GETSESS', {'ssid': resp.data['ssid']}).code, DBRespCode.OK)

    def test_UPDSESS(self):
        resp = C.send('CREATEUSR', {'name': 'sdksldks', 'passwd': '1234567'})
        resp = C.send('CREATESESS', {'uid': resp.data['uid'], 'client_ip': '123.456.789.000'})
        self.assertEqual(C.send('UPDSESS', {'ssid': resp.data['ssid']}).code, DBRespCode.OK)

    def test_DROPSESS(self):
        resp = C.send('CREATEUSR', {'name': 'sdksllllll', 'passwd': '1234567'})
        resp = C.send('CREATESESS', {'uid': resp.data['uid'], 'client_ip': '123.456.789.000'})
        self.assertEqual(C.send('DROPSESS', {'ssid': resp.data['ssid']}).code, DBRespCode.OK)


if __name__ == '__main__':
    unittest.main()
