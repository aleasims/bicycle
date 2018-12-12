import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

from core.ids.ids import  AlertParser
from core.common import load_config


def main():
    config = load_config('ids.json')

    AlertParser(config).start()

if __name__ == '__main__':
    main()
