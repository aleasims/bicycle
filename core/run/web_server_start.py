import sys
import os
sys.path.insert(0, os.path.join(os.environ['BC_DIR'], 'core'))

from web.web_server import WebServer
from common import configure_logger


def main():
    logger = configure_logger('WebServer')
    config = {}
    WebServer(config, logger).start()


if __name__ == '__main__':
    main()