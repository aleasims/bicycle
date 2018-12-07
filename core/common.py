import logging
import os
import uuid
import json
import sys


def create_unique_token(check_list, attempts=10):
    for i in range(0, attempts):
        token = uuid.uuid4().hex
        if token not in check_list:
            return token
    else:
        raise Exception('Number of attempts exceeded')


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
