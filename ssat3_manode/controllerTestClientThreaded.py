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
import json, sys, datetime,random,time, threading,csv
from os import environ
from os import path


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
    SETTEMP="/opt/storage/data/setnewtemp.csv"  
    return[CLIENTID,QID,QPWD,QHOST,QPORT,SETTEMP]

def newclient(nodeid,uid,pwd):
    ctlnodeid='controller-{}'.format(nodeid)
    mqclient=paho.Client(ctlnodeid)
    # Removing anonymous access to MQTT broker forces an attacker to gain creds
    # before they can attempt to send malicious messages 
    mqclient.username_pw_set(username=uid,password=pwd)
    # Add TLS settings when ready
    return mqclient

def newconnect(mqclient,mqhost,mqport):
    # initiate a new connection and return the status configure client values as needed
    mqconstat=mqclient.connect(mqhost,port=int(mqport),keepalive=90)
    # run as basic mqtt connection, all defaults
    #mqconstat=mqclient.connect(mqhost)
    return mqconstat

def updatecurtemp(logfile,recdict):
    with open(logfile, 'a') as jsonfh:
         json.dump(recdict,jsonfh)
         jsonfh.write('\n')
    return

def updatediaglog(logfile,recjson):
    with open(logfile, 'a') as jsonfh:
         json.dumps(recjson,jsonfh)
         jsonfh.write('\n')
    return

def on_message_write(mqclient, userdata, msg):
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
        # write to security log       
    return

def processcurtemp(nodeid,msg):
    # need to call decryption key for NODE ID in order to read payload
    print("Current Temperature for MA-Node : {} is {}".format(nodeid,str(msg.payload)))
    timestamp=datetime.datetime.now().isoformat()
    recdict={'timestamp':timestamp,'manodeid':nodeid,'curtemp':str((msg.payload).decode("utf-8"))}
    updatecurtemp('/opt/storage/logs/currenttemp.json',recdict)
    return 

def processdiagnotics(nodeid,msg):
    # need to call decryption key for NODE ID in order to read payload
    print("Diagnostics report from MA-Node : {} is {}".format(nodeid,str(msg.payload)))
    updatediaglog('/opt/storage/logs/currenttemp.json',str((msg.payload).decode("utf-8")))
    return 

def newtopicpub(mqclient,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    mqclient.publish(topic,data)
    return

def newtemppub(mqclient,topicstr,data):
    mqclient.publish(topicstr,data)
    return

def newtopictreesub(mqclient,topic):
    topic='{}/#'.format(topic)
    mqclient.subscribe(topic)
    return

def newtemp():
    curtemp=str(round(random.uniform(10.00,35.00),2))
    return curtemp

# This monitoring function needs to run as it's own thread
# collecting current temp and system diagnostics for a zone is 
# lower priority than setting a new temperature
def monitorsubscriptions(mqclient):
    mqclient.on_message = on_message_write
    # Subscribe to current temperature and diagnostics topics
    newtopictreesub(mqclient,"ct")
    newtopictreesub(mqclient,"dd")
    # begin monitoring message queues
    mqclient.loop_forever(retry_first_connection=True)

def getzonetemps(filepath):
    # stub process for changing temperature,  node-guid,temp  where temp is float 
    newzonetemps={}
    with open(filepath,'r') as csvfh:
        csv_reader = csv.reader(csvfh,delimeter=",")
        for row in csv_reader:
            topicstring='st/{}'.format(row[0])
            newzonetemps[topicstring] = row[1]
    return newzonetemps




    


def main():
    nodevars=setvars()
    thisclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    mqconstat=newconnect(thisclient,nodevars[3],nodevars[4])
    # communication failure mitigations
    comfailurecount=0
    extendedcomfailure=False
    #
    if mqconstat == 0:
            # On successful connection:
            # migrate monitoring of current temperature and diagnostics to a background thread
            subscriptionthread = threading.Thread(target=monitorsubscriptions(thisclient))
            subscriptionthread.start()
            
    elif not extendedcomfailure and comfailurecount < 10 :
            # Attempt to reconnect for ~ 20 minutes 
            while comfailurecount < 10  and mqconstat != 0:
                print("MQTT Broker connection failure, reattemp in {} seconds".format(45 * comfailurecount))
                #
                backoffinterval=(30 * comfailurecount) + random.randint(10,30)
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
    
    # presuming the monitoring thread started ok start a second loop checking for temp updates
    pubclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    while True:
        if path.exists(nodevars[5]):
            # create client only when ready to publish
            mqpubconstat=newconnect(thisclient,nodevars[3],nodevars[4])
            if mqpubconstat == 0:
                # Simulate database query, node guid as unique ID & temperature set by user
                thesetemps=getzonetemps(nodevars[5])
                for key, value in thesetemps.items():
                    newtemppub(pubclient,key,value)
                thisclient.disconnect()
        time.sleep(60)


                










if __name__=="__main__":
    main()