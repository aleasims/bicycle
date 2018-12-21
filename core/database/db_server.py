from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler
import socket
import logging
import threading
import os
import io
import queue
import traceback
from core.database.db_wrapper import DBWrapper
from core.database import db_proto


class DBServer(ThreadingMixIn, TCPServer):
    def __init__(self, config, logger):
        self.logger = logger
        self.server_address = config['server_address']
        self.storage_path = config['storage_path']
        self.session_exp_time = config['session_exp_time']
        self.max_tasks = config['max_tasks']

        self.tasks = queue.Queue(self.max_tasks)

        self.address_family = socket.AF_UNIX
        self.allow_reuse_address = True

        super().__init__(self.server_address, DBProtoHandler, True)

    def server_bind(self):
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise Exception('Cannot bind server')
        super().server_bind()

        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        self.wrapper = DBWrapper(self.logger, self.storage_path, self.session_exp_time)

    def start(self):
        self.logger.info('Server running on {}'.format(self.server_address))

        serve = threading.Thread(target=self.serve_forever)
        work = threading.Thread(target=self.do_tasks)
        serve.start()
        work.start()

    def do_tasks(self):
        while True:
            try:
                request, callback = self.tasks.get()  # blocking call
                response = self.wrapper.perform(request)
                self.logger.info('{} - {}'.format(request.method, response.code))
                conn = callback(response)
                self.shutdown_request(conn)
            except Exception as e:
                self.logger.info('Exception during task performing - {}'.format(e))
                if self.logger.level == logging.DEBUG:
                    print('*' * 80)
                    traceback.print_exc()
                    print('*' * 80)

    def process_request(self, request, client_address):
        # Need to override because no need to shutdown request
        self.finish_request(request, client_address)

    def push_task(self, request, callback):
        self.tasks.put_nowait((request, callback))


class DBProtoHandler(BaseRequestHandler):
    MAX_REQUEST_LEN = db_proto.MAX_REQUEST_LEN
    DELIMITER = db_proto.DELIMITER
    BUFSIZE = 1024

    def setup(self):
        self.raw_request = self.read_request(self.request)

    def callback(self, response):
        self.request.sendall(response.bytes)
        return self.request

    def handle(self):
        try:
            request = db_proto.Request(self.raw_request)
            self.server.push_task(request, self.callback)
        except Exception as e:
            self.server.logger.info('Exception during hadnling - {}'.format(e))
            if self.server.logger.level == logging.DEBUG:
                print('*' * 80)
                traceback.print_exc()
                print('*' * 80)

    def read_request(self, conn):
        request = bytearray()
        while True:
            try:
                request += conn.recv(self.BUFSIZE)
            except socket.timeout:
                break
            if len(request) > self.MAX_REQUEST_LEN:
                raise Exception('Too long request')
            if self.DELIMITER in request:
                break
        return request
