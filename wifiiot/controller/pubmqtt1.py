#!/usr/bin/env python3
# An MQTT beacon publisher, just sends the time every 15 seconds,
# Change host value to a broker inside a DMZ and you could push to subs in the field.
# Looks pretty cool.

# to fix, subprocess was not working right so temporarily moveing to OS system

import subprocess, time, sys, os
from datetime import datetime
# 
def gettime():
    now=datetime.now()
    return str(datetime.timestamp(now))


def genmqttmsg():
    # Need to use the python client
    ts = gettime()
    mqttpubarg = '-h 127.0.0.1 -p 4321 -t "fieldsite/ctrl_beacon" -m "' + ts + '"'  
    print(mqttpubarg)
    mqttpubcmd = "'" + "/usr/bin/mosquitto_pub " + mqttpubarg + " '"
    print(mqttpubcmd)
    os.system(mqttpubcmd)
    #subprocess.run(['/usr/bin/mosquitto_pub',mqttpubarg])
    return

while True:
    genmqttmsg()
    time.sleep(15.0)
