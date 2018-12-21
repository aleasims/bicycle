#!/bin/bash
ENV=true
if [ "$1" = "-e" ]
then
	ENV=false
fi


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR


PYTHON_VERSION=3.6
PYTHON=python$PYTHON_VERSION


if $ENV
then
	virtualenv --python=python$PYTHON_VERSION env
	source env/bin/activate	
fi

pip install tinydb

python bicycle.py
