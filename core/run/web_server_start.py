import sys
import os
sys.path.insert(0, os.environ['BC_DIR'])

from core.web.web_server import WebServer
from core.common import configure_logger, load_config


def main():
    config = load_config('web_server.json')
    logger = configure_logger(config['name'])
    WebServer(config, logger).start()


if __name__ == '__main__':
    main()