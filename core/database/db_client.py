import socket
import traceback
from core.database import db_proto


class Client:
    def __init__(self, ipc_path, logger=None):
        self.logger = logger
        self.ipc_path = ipc_path
        self.bufsize = 2048
        self.sock_timeout = 10

    def _log_err(self, e):
        message = 'Exception during interacting with DB: {}: {}'.format(
            e.__class__.__name__, e.args[0])
        if self.logger is not None:
            self.logger.info(message)
        else:
            print(message)
            traceback.print_exc()

    def send(self, method, params={}):
        # Forms request from given method and params
        # Sends it to DBServer
        # Waits for response and returns it
        #
        response = None
        ipc = socket.socket(socket.AF_UNIX)
        ipc.settimeout(self.sock_timeout)
        try:
            request = db_proto.Request(method=method,
                                       params=params).bytes
            ipc.connect(self.ipc_path)
            ipc.sendall(request)
            response = self.recvall(ipc)
        except Exception as e:
            self._log_err(e)
        finally:
            ipc.close()

        if response is not None:
            return db_proto.Response(response)

    def recvall(self, ipc):
        data = bytearray()
        while True:
            data += ipc.recv(self.bufsize)
            if db_proto.DELIMITER in data:
                break
        return bytes(data)
