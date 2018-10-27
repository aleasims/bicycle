import socket
import core.database.db_proto
from core.database.db_manager import DBManager


class ClientError(Exception):
    pass


class DBClient:
    def __init__(self, ipc_path):
        self.ipc_path = ipc_path
        self.bufsize = 2048
        self.sock_timeout = 10

    def send(self, request):
        query = request.bytes
        print('Client sending query: {}'.format(query))
        ipc = socket.socket(socket.AF_UNIX)
        ipc.settimeout(self.sock_timeout)
        try:
            ipc.connect(self.ipc_path)
        except socket.timeout:
            raise ClientError('DB is not answering')

        try:
            ipc.sendall(query)
        except InterruptedError:
            try:
                ipc.sendall(query)
            except InterruptedError:
                raise ClientError('Sending query malformed')

        response = self._recv(ipc)
        print('Client received response: {}'.format(response))
        return db_proto.Response(response)

    def _recv(self, ipc):
        data = bytearray()
        while True:
            try:
                data += ipc.recv(self.bufsize)
            except socket.timeout:
                raise ClientError('Response malformed')
            if db_proto.DELIMITER in request:
                break
        return data
