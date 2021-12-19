#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build
#                 1, built out data generation functions and queue publishing.
#                    removing load env, need to instantiate using docker run arg
#                 2, adding connection to "st" message queue used for setting temperature
#                 3, Adding payload encryption
# 
#  using paho client https://www.eclipse.org/paho/index.php?page=clients/python/index.php
#
#  Test client reads node ID and symetric key from file
#  Initiates connections to each function topic using heirarchical structure
#  Generates random payloads for each function
#  set enc=False to disable encryption
#  Run in 30-45 second loop to allow logic testing for controller
#  
############################################################

import  paho.mqtt.client as paho
import random,time
from os import environ
from cryptography.fernet import Fernet
# import custom modules
import controlUnit as cu
import appEnc as aenc
# Global variables
settempval=None # Use to track set temp values received and properly decrypted
SECRET_KEY=environ.get('SKEY128') # Need to delcare globally so MQTT callback can access


def setvars():
    # Load node specific data using environment file
    # Must start the container with --env-file 
    SECRET_KEY=environ.get('SKEY128')
    NODEID=environ.get('MANID')
    QID=environ.get('QID')
    QPWD=environ.get('QPWD')
    QHOST=environ.get('QHOST')
    QPORT=environ.get('QPORT')
    return[SECRET_KEY,NODEID,QID,QPWD,QHOST,QPORT]

def newclient(nodeid,uid,pwd):
    manodeid='manode-{}'.format(nodeid)
    mqclient=paho.Client(manodeid)
    mqclient.username_pw_set(username=uid,password=pwd)
    # Add TLS settings when ready
    return mqclient

def newconnect(mqclient,mqhost,mqport):
    # initiate a new connection and return the status configure client values as needed
    mqconstat=mqclient.connect(mqhost,port=int(mqport),keepalive=90)
    return mqconstat


def newtopicpub(mqclient,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    print("publishing {} to {}".format(data,topic))
    mqclient.publish(topic,data, qos=1,retain=True)
    return

def newtopicsub(mqclient,topic,nodeid):
        topic='{}/{}'.format(topic,nodeid)
        substat=mqclient.subscribe(topic)
        # What do we get back on client subscribe?
        return substat

# This function is a custom callback created to monitor the queue used for setting new 
# temperatures for a given node. Symetric encryption is used to provide non-repudiation 
# and data privacy. There is limited privacy impact with the disclosure of temperature information
# but the requirement to decrypt message prevents the MA-Node from processing a message that was
# not encrypted by the controller, a strong prevention against replay attacks, injection attacks 
# and so forth .
def on_msg_dcrypt(client,userdata,msg):
    result=tuple((msg.topic).split("/"))
    # only attempt decryption on messages submitted to the encrypted ST queue which likely contain encrypted data
    if result[0]=="encst":
        SECRET_KEY=environ.get('SKEY128') #Retrieve encryption key when needed at run time
        global settempval
        print('decrypt the following payload:\n{}'.format(str(msg.payload)))
        print(type(msg.payload))
        if isinstance(msg.payload,bytes):
            print('Validate message content using decryption, if message valid update global variable tracking temperature to be set')
            bytedata=msg.payload
            print(str(bytedata))
            # This function attempts to decrypt the payload data with the MA-Node symetric key
            # Function returns a byte array if decryption is successful or "None" which will
            # over-ride the global variable used to set temperatues on the actuator node.
            decpayload=decrypt_data(SECRET_KEY,bytedata)
            if decpayload:
                try:
                    # if the correct key was used the data should be a valid byte array
                    # that can be converted to a float
                    decval=float(decpayload)
                    settempval = decval
                    #print(str(settempval))
                except Exception as e:
                    print("Decryption error, terminate input processing")
                    settempval = None
                    pass
            else:
                settempval = None

# Change over to using the imported module
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


def procsettemp(msg):
    # double check message is a float value
    try:
        settemp=float((msg.payload).decode("utf-8"))
        return settemp
    except Exception as e:
        print("Invalid payload")
        print(e)
        return


def main():
    nodevars=setvars()
    # communication failure mitigations
    comfailurecount=0
    #extendedcomfailure=False
    # Diagnositcs loop control
    monitorcycle=0
    # Instantiate digital thermometer simulation
    tempsensor1 = cu.TempSensor(nodevars[1])
    # get curent temperature in controlled zone and set heating/cooling to off
    tempdata=tempsensor1.gettemp()
    cool=False
    heat=False
    
    while True:
        # check for new temperature
        subclient=newclient(nodevars[1],nodevars[2],nodevars[3])
        #subclient.on_message = on_message_update # clear text version
        enctopic='encst/{}'.format(nodevars[1])
        subclient.message_callback_add(enctopic,on_msg_dcrypt)
        mqconstat=newconnect(subclient,nodevars[4],nodevars[5])
        if mqconstat == 0:
            subclient.loop_start()
            # check for new temperature setting on "st" message queue
            print("checking encst/{} queue for new temperature".format(nodevars[1]))
            subresult=newtopicsub(subclient,"encst",nodevars[1])
            if subresult[0]==0:
                print("connected, waiting for callbacks")
                time.sleep(3)
                if isinstance(settempval,float):
                    hclist=cu.testnewtemp(settempval,tempsensor1)
                else:
                    targettemp=tempsensor1.gettargettemp()
                    hclist=cu.testnewtemp(targettemp,tempsensor1)
                cu.sethcstatus(hclist)
            else:
            # by default cool by 0.1 degrees
                tempsensor1.settemp(-0.1)
                #Ensure heating & cooling off
                heat=False
                cool=False
                hclist=[heat,cool]
                cu.sethcstatus(hclist)
        else:
            comfailurecount +=1
        # Stop & disconnect allows disconnected mode
        subclient.loop_stop()
        subclient.disconnect()
        monitorcycle+=1
          
        # Update current temperature every 3rd iteration, 
        if monitorcycle%3 == 0:
            tempdata=tempsensor1.gettemp()
            pubclient=newclient(nodevars[1],nodevars[2],nodevars[3])
            mqconstat=newconnect(pubclient,nodevars[4],nodevars[5])
            if mqconstat == 0:
                newtopicpub(pubclient,"ct",nodevars[1],tempdata[1])
                monitorcycle+=1
                pubclient.disconnect()
        # every 15-20 minutes collect diagnostics and publish them (change to 20 for prod )
        if monitorcycle >= 12:
            diagdata=cu.newdiag(nodevars[1],comfailurecount)
            pubclient=newclient(nodevars[1],nodevars[2],nodevars[3])
            mqconstat=newconnect(pubclient,nodevars[4],nodevars[5])
            if mqconstat == 0:
                newtopicpub(pubclient,"dd",nodevars[1],diagdata)
                pubclient.disconnect()
            monitorcycle=0
        # Adjust this value to 60-90 seconds in a production environment
        # Suggest applying 5-10 seconds of randomization to the looping to avoid a flood of events in the
        # scenario where a number of units all come back online at once.    
        time.sleep(random.randint(15,18))
        

if __name__=="__main__":
    main()