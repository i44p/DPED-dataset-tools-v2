#!/bin/bash

# Сохраняем текущую директорию
PREV_DIR=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
export LD_LIBRARY_PATH=$SCRIPT_DIR/../lib

## operation
echo "open session"
./control open $@

echo "authentication"
./control auth $@

echo "set the Dial mode to Host"
./control send --op=0x9205 --p1=0xD25A --size=1 --data=0x01 $@

echo "set the operating mode to still shooting mode"
./control send --op=0x9205 --p1=0x5013 --size=4 --data=0x00000001 $@

sleep 1

echo "waiting the operating mode API"

./control send --op=0x9207 --p1=0xD2C1 --data=0x0002 --size=2 $@
sleep 1.5

./control send --op=0x9207 --p1=0xD2C1 --data=0x0001 --size=2 $@
sleep 2

# Закрываем сессию
echo "close session"
./control close $@


# Возвращаемся в предыдущую директорию
cd $PREV_DIR
