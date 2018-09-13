import sys
import os
sys.path.insert(0, os.path.join(os.environ['BC_DIR'], 'core'))

from web.web_server import WebServer
from common import configure_logger, load_config


def main():
    config = load_config('web_server.json')
    logger = configure_logger(config['name'])
    WebServer(config, logger).start()


if __name__ == '__main__':
    main()