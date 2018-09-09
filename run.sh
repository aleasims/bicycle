SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_VERSION=3.6
echo $SCRIPT_DIR

cd $SCRIPT_DIR

python$PYTHON_VERSION bicycle.py