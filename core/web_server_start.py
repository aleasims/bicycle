from core.web.web_server import WebServer
from core.common import configure_logger


def main():
    logger = configure_logger('WebServer')
    config = {}
    WebServer(config, logger).start()


if __name__ == '__main__':
    main()