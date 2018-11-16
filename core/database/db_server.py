import time
import socket
import os
import traceback
from core.database import db_proto
from core.database.db_wrapper import DBWrapper


class DBServer:
    '''
    Accepts queries to database and 
    sends them to handling into DB (wrapper)
    '''
    def __init__(self, config, logger):
        self.logger = logger
        self.ipc_path = config['ipc_path']
        self.type = config['type']
        self.session_exp_time = config['session_exp_time']
        self.conn_timeout = config['connection_timeout']
        self.storage_path = config['storage_path']

        self.BACKLOG = 5
        self.BUFSIZE = 1024
        self.MAX_REQUEST_LEN = 2048
        self.DELIMITER = db_proto.DELIMITER

    def start(self):
        if not self.init():
            self.logger.error('Failed to run server')
            return
        self.main_loop()

    def init(self):
        try:
            os.unlink(self.ipc_path)
        except OSError:
            if os.path.exists(self.ipc_path):
                return False
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        self.wrapper = DBWrapper(self.logger, self.storage_path, self.session_exp_time)

        self.ipc = socket.socket(socket.AF_UNIX)
        try:
            self.ipc.bind(self.ipc_path)
            self.ipc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ipc.listen(self.BACKLOG)
        except socket.error:
            return False
        return True

    def main_loop(self):
        self.logger.info('Server running on {}'.format(self.ipc_path))
        while True:
            (conn, address) = self.ipc.accept()
            conn.settimeout(self.conn_timeout)
            try:
                self.handle(conn, address)
            except Exception as e:
                self.logger.warning('Exception during handling request: {}'.format(e))
                traceback.print_exc()
            finally:
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()

    def handle(self, conn, address):
        t = time.time()
        request = db_proto.Request(self.get_request(conn))
        response = self.wrapper.perform(request)
        conn.sendall(response.bytes)

        self.logger.info('{} - {} ({}s)'.format(
            request.method, response.code, round(time.time() - t, 7)))

    def get_request(self, conn):
        request = bytearray()
        while True:
            try:
                request += conn.recv(self.BUFSIZE)
            except socket.timeout:
                break
            if self.DELIMITER in request:
                break
            if len(request) > self.MAX_REQUEST_LEN:
                raise Exception('Too long request')
        return request
