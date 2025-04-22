#!/bin/bash

# Сохраняем текущую директорию
PREV_DIR=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
export LD_LIBRARY_PATH=$SCRIPT_DIR/../lib


sleep 1.5

echo "Focusing..."

# Half-Release Down
./control send --op=0x9207 --p1=0xD2C1 --data=0x0002 --size=2 $@

sleep 1.5


# Возвращаемся в предыдущую директорию
cd $PREV_DIR
