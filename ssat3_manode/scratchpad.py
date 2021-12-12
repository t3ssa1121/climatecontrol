#!/usr/bin/env python3
#  Author(s): Doug Leece 

import  paho.mqtt.client as paho
from cryptography.fernet import Fernet
import json, sys, datetime,random,time

# vars for functions
skey128="lDiXfxjF3Ok4CpBmswBjV2rbI5LqQyJzBqJqHCWEAXs="   # this is pulled from ENV on startup normally
settempval=None # Use to track set temp values received and properly decrypted


# This function is a custom callback created to monitor the queue used for setting new 
# temperatures for a given node. Symetric encryption is used to provide non-repudiation 
# and data privacy. There is limited privacy impact with the disclosure of temperature information
# but the requirement to decrypt message prevents the MA-Node from processing a message that was
# not encrypted by the controller, a strong prevention against replay attacks, injection attacks 
# and so forth .
def on_msg_dcrypt(client,userdata,msg):
    result=tuple((msg.topic).split("/"))
    # only attempt decryption on messages submitted to the encrypted ST queue which likely contain encrypted data
    if result[0]=="enctst":
        global settempval
        print("currentsettempval:{}".format(str(settempval)))
        print('decrypt me: {}'.format(str(msg.payload)))
        print(type(msg.payload))
        if isinstance(msg.payload,bytes):
            print('Validate message content using decryption, if message valid update global variable tracking temperature to be set')
            bytedata=msg.payload
            print(str(bytedata))
            # This function attempts to decrypt the payload data with the MA-Node symetric key
            # Function returns a byte array if decryption is successful or "None" which will
            # over-ride the global variable used to set temperatues on the actuator node.
            decpayload=decrypt_data(skey128,bytedata)
            if decpayload:
                try:
                    # if the correct key was used the data should be a valid byte array
                    # that can be converted to a float
                    decval=float(decpayload)
                    settempval = decval
                    print(str(settempval))
                except Exception as e:
                    print("Decryption error, terminate input processing")
                    settempval = None
                    pass
            else:
                settempval = None
    #else:
    #    print("empty queue message")
    #    settempval = None


def decrypt_data(keystr,data):
    bytekey=bytes(keystr,'utf-8')
    enchandle=Fernet(bytekey)
    try:
        decbytes=enchandle.decrypt(data)
        return decbytes
    except Exception as e:
        print("Payload not encrypted with authorized key")
        pass
        return None

def encrypt_data(keystr,data):
    bytekey=bytes(keystr,'utf-8')
    enchandle=Fernet(bytekey)
    encbytes=enchandle.encrypt(data)
    return encbytes



def newclient(nodeid,uid,pwd):
    manodeid='manode-{}'.format(nodeid)
    mqclient=paho.Client(manodeid, clean_session=True, userdata=None)
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
                print("currentsettempval:{}".format(str(settempval)))
                if isinstance(settempval,float):
                    print("submit this settemp {} to climate control unit".format(settempval))
                else:
                    print("get last known good temp and submit that")
            subclient.loop_stop()
            subclient.disconnect()
            global settempval
            settempval=None  #reset through each iteration to ensure an empty queue doesn't affect operation
        time.sleep(30)

if __name__=="__main__":
    main()