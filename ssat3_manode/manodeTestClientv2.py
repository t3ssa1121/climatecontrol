#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build
#                 1, built out data generation functions and queue publishing.
#                    removing load env, need to instantiate using docker run arg
#                 2, adding retain to leave the messages on the queue  
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
import json, sys, datetime,random,time
from os import environ, path
#from dotenv import load_dotenv


def setvars():
    # Load node specific data using environment file
    # Must start the container with --env-file 
    #basedir = path.abspath(path.dirname(__file__))
    #load_dotenv(path.join(basedir,'.env'))
    #load_dotenv('opt/src/.env')
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
    # run as basic mqtt connection, all defaults
    #mqconstat=mqclient.connect(mqhost)
    return mqconstat

def on_connect(client,userdata,flags,rc):
    # confirm connection worked, print response code
    if rc==0:
        print("Successful connection to broker")
    else:
        print("Connection failed, rc: " +connack_strin(rc))

def newtopicpub(mqclient,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    mqclient.publish(topic,data, qos=1,retain=True)
    return

def newtemp():
    curtemp=str(round(random.uniform(10.00,35.00),2))
    return curtemp

def newdiag(nodeid,comstats):
    # simulation of collect maintenamce information from sensors
    # Send as a JSON string 
    sensor1=str(round(random.uniform(123.00,412.00),2))
    sensor2=str(random.randint(12,106))
    timestamp=datetime.datetime.now().isoformat()
    # create dictionary then dump to json string
    diagdata={}
    diagdata["manode_time"]=timestamp
    diagdata["manode_id"]=nodeid
    diagdata["sensor1"]=sensor1
    diagdata["sensor2"]=sensor2
    diagdata["comstats"]=comstats
    diagdatajson = json.dumps(diagdata)
    return diagdatajson



def main():
    nodevars=setvars()
    thisclient=newclient(nodevars[1],nodevars[2],nodevars[3])
    mqconstat=newconnect(thisclient,nodevars[4],nodevars[5])
    # communication failure mitigations
    comfailurecount=0
    extendedcomfailure=False
    # Diagnositcs loop control
    monitorcycle=0
    # test loop
    while True:
        # get curent temperature in controlled zone
        tempdata=newtemp()
        if mqconstat == 0:
            newtopicpub(thisclient,"ct",nodevars[1],tempdata)
            # to do: test to make sure the temp was sent
            monitorcycle+=1
            time.sleep(random.randint(35,48))
        # every 15-20 minutes collect diagnostics and publish them (change to 20 for prod )
            if monitorcycle >= 10:
                diagdata=newdiag(nodevars[1],comfailurecount)
                newtopicpub(thisclient,"dd",nodevars[1],diagdata)
                monitorcycle=0
        # Retry communications several times since network outages ofen only last minutes
        elif not extendedcomfailure:
            comfailurecount+=1
            monitorcycle+=1  # continue to count intervals for diag
            print("MQTT Broker connection failure, reattemp in {} seconds".format(45 * comfailurecount))
            #to do: move to function, increase backoff interval 
            #       based on counter and set exit flag on max
            #       include random delay per node to avoid all nodes
            #       retrying at exactly the same time, (E.G. building power outage)
            backoffinterval=(45 * comfailurecount) + random.randint(10,30)
            time.sleep(backoffinterval)
            #initiate a reconnection
            # Not sure we need a new object
            #thisclient=newclient(nodevars[1],nodevars[2],nodevars[3])
            mqconstat=newconnect(thisclient,nodevars[4],nodevars[5])
            time.sleep(5)
        else:
            # During an extended outage avoid flooding the network with traffic,
            # This could be a significant load if several hundred nodes were down
            # aggrevating restoration efforts
            #to do: intelligent retry function that checks every hour to reset
            #       extended failed comms condition. Collect diags to submit on reconnection
            print("Warning: extended communications failure")
            print("Maintaining current climate control programming")
            print("Contact 1-800-noqtemp to report outage")
            time.sleep(600)


    


if __name__=="__main__":
    main()