#!/usr/bin/env python3
#  Author(s): Doug Leece 

import  paho.mqtt.client as paho
import json, sys, datetime,random,time

settempval='' # Use to track set temp values received and properly decrypted

def on_msg_dcrypt(client,userdata,msg):
    result=tuple((msg.topic).split("/"))
    # only attempt decryption on messages which likely contain encrypted data
    if result[0]=="enctst":
        print('decrypt me: {}'.format(str(msg.payload)))
        print('if message valid update global variable tracking temperature to be set')
        decryptedval=float(23.67)
        global settempval
        settempval = decryptedval



def newclient(nodeid,uid,pwd):
    manodeid='manode-{}'.format(nodeid)
    mqclient=paho.Client(manodeid, clean_session=True, userdata=None,protocol=MQTTv311,transport="tcp")
    mqclient.username_pw_set(username=uid,password=pwd)
    # Add TLS settings when ready
    return mqclient

def newconnect(mqclient,mqhost,mqport):
    # initiate a new connection and return the status configure client values as needed
    mqconstat=mqclient.connect(mqhost,port=int(mqport),keepalive=90)
    return mqconstat

def newtopicsub(mqclient,topic,nodeid):
        topic='{}/{}'.format(topic,nodeid)
        substat=mqclient.subscribe(topic, qos=1)
        # What do we get back on client subscribe?
        return substat

def main():


    while True:
        subclient=newclient('000lab23','nodetester','changeme')
        # specifies exact queue to be monitoring
        subclient.message_callback_add('enctst/000lab23',on_msg_dcrypt)
        mqconstat=newconnect(subclient,'10.100.200.3','1883')
        if mqconstat == 0:
            subclient.loop_start()
            substats=newtopicsub(subclient,'enctst','000lab23')
            if substats[0]==0:
                print("monitor queue for new messages")
                time.sleep(3) # allow time for message collection, decryption & processing
                if isinstance(settempval,float):
                    print("submit settemp to climate control unit")
                else:
                    print("get last known good temp and submit that")
            subclient.loop_stop()
            subclient.disconnect()
        time.sleep(30)
