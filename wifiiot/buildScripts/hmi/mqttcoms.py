#!/usr/bin/env python3
#import paho.mqtt.client as mqtt
#import sys
import json


# Move command line args to a function
def mqttpub(opdir,optime,opdevice,opclient):
    ctrldict = dict()
    ctrldict['direction']=opdir
    ctrldict['duration']=optime
    ctrldict['device']=opdevice
    ctrljson = json.dumps(ctrldict)
    opclient.publish(topic="fieldsite/ctrl_motor",payload=ctrljson,qos=1, retain=False)
    return