import os
import sys
import signal
import subprocess
from core import common
from core.common import load_config


CHILD_PROCESSES = []


def register_signal_handler(signum):
    def handler(signum, frame):
        for proc in CHILD_PROCESSES:
            proc.send_signal(signum)
        signal.SIG_DFL
    signal.signal(signum, handler)


def start_modules(config):
    python_version = config['python_version']
    python = ''.join(['python', str(python_version)])

    run_dir = os.path.join(sys.path[0], 'run')
    modules = config['modules']

    debug = True if config.get('debug') else False
    output_dir = config['output_dir']

    for module in modules:
        script_name = '_'.join([module, 'start.py'])
        args = [python, os.path.join(run_dir, script_name),
                '-o', output_dir]
        if debug:
            args.append('-v')
        CHILD_PROCESSES.append(subprocess.Popen(args))

    for proc in CHILD_PROCESSES:
        proc.wait()


def main():
    register_signal_handler(signal.SIGINT)
    config = load_config('general.json')
    start_modules(config)


if __name__ == '__main__':
    main()
