import logging
import os
import json
import sys
from core.database import db_client
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v',
                        action='store_true',
                        help='verbosity level')
    parser.add_argument('-o',
                        type=str,
                        default='.',
                        help='output dir')
    args = parser.parse_args()
    return args


def configure_logger(name, debug=False, output_dir='.'):
    level = logging.DEBUG if debug else logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()

    filename = os.path.join(output_dir, 'bicycle.log')
    fh = logging.FileHandler(filename)

    canvas = '[%(asctime)s] %(name)s: %(levelname)s - %(message)s'
    formatter = logging.Formatter(canvas)

    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.debug('Logger configured')
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
