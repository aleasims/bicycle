import logging


def configure_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    canvas = '[%(asctime)s] %(name)s: %(levelname)s - %(message)s'
    formatter = logging.Formatter(canvas)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger