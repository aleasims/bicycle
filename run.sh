SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
STATIC_DIR=$SCRIPT_DIR/www


export BC_DIR=$SCRIPT_DIR
export BC_STATIC_DIR=$STATIC_DIR


PYTHON_VERSION=3.6
cd $SCRIPT_DIR


python$PYTHON_VERSION bicycle.py
