import sys
import os
# terrible style
sys.path.append(os.environ['BC_DIR'])

import subprocess

MODULES = ['db_manager']


CHILD_PROCESSES = []


def main():
    for module in MODULES:
        arg = '_'.join([module, 'start.py'])
        full_arg = '/'.join(['core', arg])
        args = ['python3', full_arg]
        CHILD_PROCESSES.append(subprocess.Popen(args))

    for proc in CHILD_PROCESSES:
        proc.poll()


if __name__ == '__main__':
    main()
