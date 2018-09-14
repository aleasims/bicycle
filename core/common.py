import logging
import os
import json

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


def load_config(file_name):
    path = os.path.join("core", "config", file_name)
    return json.load(open(path))
