import logging
import os
import json
import sys


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
    config_dir = os.path.join(sys.path[0], 'config')
    path = os.path.join(config_dir, file_name)
    return json.load(open(path))


def format(obj, max_size):
    # Slicer
    # Supports in cases of large output
    tmp = obj.__repr__()
    if len(tmp) > max_size:
        tmp = tmp[:max_size]
        tmp += '...'
    return tmp
