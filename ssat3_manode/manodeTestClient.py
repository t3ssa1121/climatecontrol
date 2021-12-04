#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build
# 
#  using paho client https://www.eclipse.org/paho/index.php?page=clients/python/index.php
#
#  Test client reads node ID and symetric key from file
#  Initiates connections to each function topic using heirarchical structure
#  Generates random payloads for each function
#  set enc=False to disable encryption
#  Run in 15 second loop to allow logic testing for controller
#  
############################################################

import  paho.mqtt.client as paho
import json, sys, datetime,random,time
from os import environ, path
from dotenv import load_dotenv


def setvars():
    # Load node specific data using environment file
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir,'.env'))
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
    mqconnect=mqclient.connect(mqhost,port=mqport,keepalive=120)
    #mqconnect=mqclient.connect(mqhost)
    return mqconnect

def on_connect(client,userdata,flags,rc):
    # confirm connection worked, print response code
    if rc==0:
        print("Successful connection to broker")
    else:
        print("Connection failed, rc: " +connack_strin(rc))

def topicpub(connected,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    connected.publish(topic,data)
    return

def newtemp():
    curtemp=str(round(random.uniform(10.00,35.00),2))
    return curtemp





def main():
    nodevars=setvars()
    thisclient=newclient(nodevars[1],nodevars[2],nodevars[3])
    thisconnect=newconnect(thisclient,nodevars[4],nodevars[5])
    # test loop
    thisconnect.loop_start()
    while True:
        tempdata=newtemp()
        topicpub(thisconnect,"ct",nodevars[1],tempdata)
        time.sleep(random.randint(5,45))


    


if __name__=="__main__":
    main()