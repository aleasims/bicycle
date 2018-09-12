from database.db_manager import DBManager
from common import configure_logger


def main():
    logger = configure_logger('DBManager')
    config = {}
    DBManager(config, logger).start()


if __name__ == '__main__':
    main()
