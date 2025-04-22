#! /bin/bash


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

sleep 1

echo "set the Dial mode to Host"
./control send --op=0x9205 --p1=0xD25A --size=1 --data=0x01 $@

sleep 1

echo "set the operating mode to still shooting mode"
./control send --op=0x9205 --p1=0x5013 --size=4 --data=0x00000001 $@

sleep 1

value="00001"

echo "change ExpMode to 0x$value (current is 0x$current)"
./control send --op=0x9205 --p1=0x500E --size=4 --data=0x$value

sleep 5

echo "close session"
./control close $@
