#!/bin/bash
# Temp work around while writing the python publisher

while true ; do

    timestamp=`date +%R:%m:%S.%N`
    /usr/bin/mosquitto_pub -h 127.0.0.1 -p 4321 -t "fieldsite/ctrl_beacon" -m ${timestamp}
    sleep 15
    done