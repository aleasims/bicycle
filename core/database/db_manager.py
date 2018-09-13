import time


class DBManager:
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

    def start(self):
        while True:
            self.logger.warning('My config: {}'.format(self.config))
            time.sleep(self.config['period'])
