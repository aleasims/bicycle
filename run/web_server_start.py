import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

from core.web.server import WebServer
from core.common import configure_logger, load_config


def main():
    config = load_config('web_server.json')
    logger = configure_logger(config['name'])
    os.environ['BC_DIR'] = sys.path[0]
    WebServer(config, logger).start()


if __name__ == '__main__':
    main()
