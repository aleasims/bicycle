from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler
import socket
import logging
from threading import Thread
import os
import io
from queue import Queue, Empty
import traceback
from core.database.db_wrapper import DBWrapper
from core.database import db_proto


class DBServer(ThreadingMixIn, TCPServer):
    def __init__(self, config, logger):
        self.logger = logger
        self.server_address = config['server_address']
        self.storage_path = config['storage_path']
        self.session_exp_time = config['session_exp_time']

        self.queue = Queue(1000)

        self.address_family = socket.AF_UNIX
        self.allow_reuse_address = True

        super().__init__(self.server_address, Handler, True)

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

        serve = Thread(target=self.serve_forever)
        work = Thread(target=self.check_queue)
        serve.start()
        work.start()

    def check_queue(self):
        while True:
            query = self.queue.get()
            request, callback = query
            response = self.wrapper.perform(request)
            conn = callback(request, response)
            self.shutdown_request(conn)

    def process_request(self, request, client_address):
        # Need to override because no need to shutdown request
        self.finish_request(request, client_address)

    def service_actions(self):
        pass

    def add_query(self, request, callback):
        self.queue.put((request, callback))


class Handler(BaseRequestHandler):
    MAX_REQUEST_LEN = db_proto.MAX_REQUEST_LEN
    DELIMITER = db_proto.DELIMITER
    BUFSIZE = 1024

    def setup(self):
        self.raw_request = self.read_request(self.request)

    def callback(self, request, response):
        self.request.sendall(response.bytes)
        self.server.logger.info('{} - {}'.format(request.method, response.code))
        return self.request

    def handle(self):
        try:
            request = db_proto.Request(self.raw_request)
            self.server.add_query(request, self.callback)
        except Exception as e:
            self.server.logger.info('Exception during hadnling - {}'.format(e))
            if self.server.logger.level == logging.DEBUG:
                traceback.print_exc()

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
