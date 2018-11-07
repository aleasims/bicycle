import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

from core.database.db_manager import DBServer
from core.common import configure_logger, load_config


def main():
    config = load_config('db_server.json')
    logger = configure_logger(config['name'])
    DBServer(config, logger).start()


if __name__ == '__main__':
    main()
