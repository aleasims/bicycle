#!/bin/bash
ENV=false
if [ "$1" = "-e" ]
then
	ENV=true
fi


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
STATIC_DIR=$SCRIPT_DIR/www
cd $SCRIPT_DIR


export BC_DIR=$SCRIPT_DIR
export BC_STATIC_DIR=$STATIC_DIR


PYTHON_VERSION=3.6
PYTHON=python$PYTHON_VERSION


if $ENV
then
	virtualenv --python=python$PYTHON_VERSION env
	source env/bin/activate	
fi


$PYTHON -B bicycle.py
