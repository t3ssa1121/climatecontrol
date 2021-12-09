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
from multiprocessing import Process
from mysql.connector import connect, Error


def setvars():
    #CLIENTID=environ.get('CLIENTID')
    #QID=environ.get('QID')
    #QPWD=environ.get('QPWD')
    #QHOST=environ.get('QHOST')
    #QPORT=environ.get('QPORT')
    #DBHOST=environ.get('DBHOST')
    #DBUSER=environ.get('DBUSER')
    #DBPWD=environ.get('DBPWD')
    #DBINST=environ.get('DBINST')
    # temp standalone testing
    CLIENTID='123456'
    QID="nodetester"
    QPWD="changeme"
    QHOST="10.100.200.3"
    QPORT="1883"
    SETTEMP="/opt/storage/data/setnewtemp.csv"
    DBHOST="10.100.200.3"
    DBUSER="lpappuser"
    DBPWD="changeme"
    DBINST="qtempapp"
    return[CLIENTID,QID,QPWD,QHOST,QPORT,SETTEMP,DBHOST,DBUSER,DBPWD,DBINST]

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

def getdbconnection(dbhost,dbuser,dbcred,dbinst):
    try:
        thisdbhandle = connect(host=dbhost,user=dbuser,password=dbcred,database=dbinst)
        return thisdbhandle
    except Error as e:
        print(e)

def newcurtempsql(nodeid,curtemp):
    sqlstr='update nodedatatmp set curtemp={} where manodeguid="{}";'.format(curtemp,nodeid)
    return sqlstr

def updatecurtemp(logfile,recdict):
    # Write to logfile
    with open(logfile, 'a') as jsonfh:
         json.dump(recdict,jsonfh)
         jsonfh.write('\n')
    # Write to database
    nodevars=setvars()
    dbconnect=getdbconnection(nodevars[6],nodevars[7],nodevars[8],nodevars[9])
    #confirm connection before generating SQL
    if dbconnect:
        newsql=newcurtempsql(recdict['manodeid'],recdict['curtemp'])
        with dbconnect.cursor() as cursor:
            cursor.execute(newsql)
            dbconnect.commit()
    return


def updatediaglog(logfile,recjson):
    with open(logfile, 'a') as jsonfh:
         jsonfh.write(recjson)
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
    updatediaglog('/opt/storage/logs/ma-node_diags.json',str((msg.payload).decode("utf-8")))
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

def getzonetemps(filepath):
    # Convert to database query, then encrypt payload, then publish to node's st queue
    # stub process for changing temperature,  node-guid,temp  where temp is float 
    newzonetemps={}
    with open(filepath,'r') as csvfh:
        csv_reader = csv.reader(csvfh,delimeter=",")
        for row in csv_reader:
            topicstring='st/{}'.format(row[0])
            newzonetemps[topicstring] = row[1]
    return newzonetemps



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
    #while True:
    #    print("I would be checking the two queue trees but")
    #    time.sleep(45)

        #return
    return

def monitorsettemp(nodevars):
    #print("now start checking temperature")
    pubclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    while True:
        print("checking for new temperature changes in {} ".format(nodevars[5]))
        if path.exists(nodevars[5]):
            print("processing new file")
            # create client only when ready to publish
            #mqpubstat=newconnect(pubclient,nodevars[3],nodevars[4])
            #if mqpubstat == 0:
            #    # Simulate database query, node guid as unique ID & temperature set by user
            #    thesetemps=getzonetemps(nodevars[5])
            #    for key, value in thesetemps.items():
            #        newtemppub(pubclient,key,value)
            #pubclient.disconnect()
        time.sleep(30)
        return



def main():
    nodevars=setvars()
    subclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    mqsubstat=newconnect(subclient,nodevars[3],nodevars[4])
    # communication failure mitigations
    comfailurecount=0
    extendedcomfailure=False
    #
    if mqsubstat == 0:
            # On successful connection:
            # migrate monitoring of current temperature and diagnostics to a background thread
            subscriptionthread = threading.Thread(target=monitorsubscriptions(subclient))
            subscriptionthread.start()
            #subproc=Process(target=monitorsubscriptions(subclient))
            #subproc.start()
            # presuming the monitoring thread started ok start a second loop checking for temp updates
            #pubtopicthread = threading.Thread(target=monitorsettemp(nodevars))
            #pubtopicthread.start()
            #pubproc=Process(target=monitorsettemp(nodevars))
            #pubproc.start()
            #
            #subproc.join()
            #pubproc.join()
            
            
    elif not extendedcomfailure and comfailurecount < 10 :
            # Attempt to reconnect for ~ 20 minutes 
            while comfailurecount < 10  and mqconstat != 0:
                print("MQTT Broker connection failure, reattemp in {} seconds".format(45 * comfailurecount))
                #
                backoffinterval=(30 * comfailurecount) + random.randint(10,30)
                time.sleep(backoffinterval)
                mqconstat=newconnect(subclient,nodevars[3],nodevars[4])
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