#!/bin/bash

PREV_DIR=$(pwd)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
export LD_LIBRARY_PATH=$SCRIPT_DIR/../lib

# fifo
FIFO=fifo$$
handler_interrupt() {
    kill $(jobs -p) >& /dev/null
    exit
}
handler_exit() {
    rm -f $FIFO
    exit
}
trap handler_interrupt INT
trap handler_exit EXIT
mkfifo -m 644 $FIFO

# common function
get_event_code() {
    TMP=`echo $2 | sed -e ':a; $!N; $!b a'`
    echo $TMP | sed -e "s/^.*$1=\([^,.]\+\).*\$/\1/g"
}

get_device_property_value() {
    TMP=`echo $2 | sed -e ':a; $!N; $!b a'`
    echo $TMP | sed -e "s/^.*$1\([0-9A-F]\+\).*\$/\1/g"
}

## operation
echo "open session"
./control open $@

echo "authentication"
./control auth $@

echo "set the Dial mode to Host"
./control send --op=0x9205 --p1=0xD25A --size=1 --data=0x01 $@

sleep 1

echo "set the operating mode to still shooting mode"
./control send --op=0x9205 --p1=0x5013 --size=4 --data=0x00000001 $@

sleep 1

echo "set savemedia to host device"
./control send --op=0x9205 --p1=0xD222 --size=2 --data=0x0001 $@

sleep 1

echo "shooting"
./control send --op=0x9207 --p1=0xD2C1 --data=0x0002 --size=2 $@
sleep 1.5
./control send --op=0x9207 --p1=0xD2C2 --data=0x0002 --size=2 $@
sleep 1.5
./control send --op=0x9207 --p1=0xD2C2 --data=0x0001 --size=2 $@
sleep 1.5
./control send --op=0x9207 --p1=0xD2C1 --data=0x0001 --size=2 $@
echo "waiting the event of adding a image"
COMPLETE=0x8000
cond="0x0000"
while [ $(($cond & $COMPLETE)) -ne $(($COMPLETE)) ]
do
    ./control get 0xD215 $@ --of=$FIFO & out=`cat $FIFO`
    echo "out"
    echo $out
    cond=0x`get_device_property_value "CurrentValue: " "$out"`
    echo "cond"
    echo $cond
done

sleep 1
echo "getobjectinfo"
./control recv --op=0x1008 --p1=0xffffc001 $@
echo "getobject"
./control getobject 0xffffc001 $@ --of=shoot.jpg

sleep 5

./control close $@

cd $PREV_DIR
