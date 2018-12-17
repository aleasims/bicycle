import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

from core.database.db_server import DBServer
from core.common import configure_logger, load_config, parse_args


def main():
    config = load_config('db_server.json')
    args = parse_args()
    logger = configure_logger(config['name'], args.v, args.o)
    DBServer(config, logger).start()


if __name__ == '__main__':
    main()
