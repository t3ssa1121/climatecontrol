#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build  (Dec 5, 2021)
#                   
# 
#  using paho client https://www.eclipse.org/paho/index.php?page=clients/python/index.php
#
#  Test client reads all node ID and symetric key from file
#  Initiates subscribing connections to each function topic using heirarchical structure
#  Generates random temperate change requests for each node
#  set enc=False to disable encryption
#  Run in 30-45 second loop to allow logic testing for controller
#  
############################################################

import  paho.mqtt.client as paho
import json, sys, datetime,random,time, threading
from os import environ


def setvars():
    #CLIENTID=environ.get('CLIENTID')
    #QID=environ.get('QID')
    #QPWD=environ.get('QPWD')
    #QHOST=environ.get('QHOST')
    #QPORT=environ.get('QPORT')
    # temp standalone testing
    CLIENTID='123456'
    QID="nodetester"
    QPWD="testINprod"
    QHOST="10.100.200.3"
    QPORT="1883"  
    return[CLIENTID,QID,QPWD,QHOST,QPORT]

def newclient(nodeid,uid,pwd):
    ctlnodeid='controller-{}'.format(nodeid)
    mqclient=paho.Client(ctlnodeid)
    # Removing anonymous access to MQTT broker forces an attacker to gain creds
    # before they can attempt to send malicious messages 
    mqclient.username_pw_set(username=uid,password=pwd)
    # MQTT supports wildcard based topics which simplifies subscription
    #mqclient.subscribe("ct/#")
    #mqclient.subscribe("dd/#")
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

def on_message(mqclient, userdata, msg):
    # when message is recieved on a queue that is subscribed to this callback event fires
    # read the content of the message, call functions based on content
    if userdata is not None:
        print("UserData included: {}".format(userdata))
    result=tuple((msg.topic).split("/"))
    if result[0]=="ct":
        processcurtemp(result[1],msg)
    elif result[0]=="dd":
        processdiagnotics(result[1],msg) 
    else:
        print("warning undefined topic: {}".format(msg.topic))       
    return


def on_message_write(mqclient, userdata, msg):
    # when message is recieved on a queue that is subscribed to this callback event fires
    # read the content of the message, call functions based on content
    if userdata is not None:
        print("UserData included: {}".format(userdata))
    result=tuple((msg.topic).split("/"))
    if result[0]=="ct":
        processcurtemp(result[1],msg)
        # get data back & append to file
    elif result[0]=="dd":
        processdiagnotics(result[1],msg)
        # get data back & append to file  
    else:
        print("warning undefined topic: {}".format(msg.topic))
        # write to security log       
    return

def processcurtemp(nodeid,msg):
    # need to call decryption key for NODE ID in order to read payload
    print("Current Temperature for MA-Node : {} is {}".format(nodeid,str(msg.payload)))
    return

def processdiagnotics(nodeid,msg):
    # need to call decryption key for NODE ID in order to read payload
    print("Diagnostics report from MA-Node : {} is {}".format(nodeid,str(msg.payload)))
    return

def newtopicpub(mqclient,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    mqclient.publish(topic,data)
    return

def newtopictreesub(mqclient,topic):
    topic='{}/#'.format(topic)
    mqclient.subscribe(topic)
    return

def newtemp():
    curtemp=str(round(random.uniform(10.00,35.00),2))
    return curtemp

def monitorsubscriptions(mqclient):
    mqclient.on_message = on_message_write
    # Subscribe to current temperature and diagnostics topics
    newtopictreesub(mqclient,"ct")
    newtopictreesub(mqclient,"dd")
    # begin monitoring message queues
    mqclient.loop_forever(retry_first_connection=True)


    


def main():
    nodevars=setvars()
    thisclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    mqconstat=newconnect(thisclient,nodevars[3],nodevars[4])
    # communication failure mitigations
    comfailurecount=0
    extendedcomfailure=False
    # Diagnositcs loop control
    #monitorcycle=0
    #
    if mqconstat == 0:
            # On successful connection:
            # assign on message callback to client and 
            monitorsubscriptions(thisclient)
            #thisclient.on_message = on_message
            ## Subscribe to current temperature and diagnostics topics
            #newtopictreesub(thisclient,"ct")
            #newtopictreesub(thisclient,"dd")
            ## begin monitoring message queues
            #thisclient.loop_forever(retry_first_connection=True)
        
    elif not extendedcomfailure and comfailurecount < 10 :
            while comfailurecount < 10 :
                print("MQTT Broker connection failure, reattemp in {} seconds".format(45 * comfailurecount))
                #
                backoffinterval=(45 * comfailurecount) + random.randint(10,30)
                time.sleep(backoffinterval)
                mqconstat=newconnect(thisclient,nodevars[3],nodevars[4])
                time.sleep(5)
                comfailurecount+=1    


    else:
            extendedcomfailure = True
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