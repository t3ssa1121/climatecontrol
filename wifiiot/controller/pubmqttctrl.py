#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import sys
import json

# Config dest IP and port
brkrurl = '192.168.59.11'
brkrport = 4321
args=sys.argv[1:]

direction=args[0]
duration=args[1]
autdevid=args[2]
ctrldict = dict()
ctrldict['direction']=direction
ctrldict['duration']=duration
ctrldict['device']=autdevid
ctrljson = json.dumps(ctrldict)
client = mqtt.Client()
client.connect(brkrurl,brkrport)
client.publish(topic="fieldsite/ctrl_motor",payload=ctrljson,qos=1, retain=False)