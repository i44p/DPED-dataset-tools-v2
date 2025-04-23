#!/bin/bash

# Сохраняем текущую директорию
PREV_DIR=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
export LD_LIBRARY_PATH=$SCRIPT_DIR/../lib

sleep 5

./control close $@

sleep 3

cd $PREV_DIR
