import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

from core.database.db_manager import DBManager
from core.common import configure_logger, load_config


def main():
    config = load_config('db_manager.json')
    logger = configure_logger(config['name'])
    DBManager(config, logger).start()


if __name__ == '__main__':
    main()
