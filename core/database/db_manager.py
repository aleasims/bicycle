import logging
import time


class DBManager:
    def __init__(self, config, logger):
        self.logger = logger

    def start(self):
        while True:
            self.logger.warning('hello from db')
            time.sleep(3)