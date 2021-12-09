#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build  (Dec 8, 2021)
#                   
# Stripped down to get simple pub & sub in same script


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

# MQTT client functions 
# configure client connection so it is uniquely identified and also has a username and password applied
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
    mqconstat=mqclient.connect(mqhost,port=int(mqport),keepalive=120)
    # run as basic mqtt connection, all defaults
    #mqconstat=mqclient.connect(mqhost)
    return mqconstat

def on_message_write(mqclient, userdata, msg):
    # when message is recieved on a queue that is subscribed to this callback event fires
    # read the content of the message, call functions based on content
    if userdata is not None:
        print("UserData included: {}".format(userdata))
    result=tuple((msg.topic).split("/"))
    if result[0]=="ct":
        #print("Received current temp from {} : {}".format(result[1],str(msg.payload)))
        processcurtemp(result[1],msg)
    elif result[0]=="dd":
        #print("Received diagnostics from {} : {}".format(result[1],str(msg.payload)))
        processdiagnotics(result[1],msg)
    else:
        print("warning undefined topic: {}".format(msg.topic))
        # write to security log       
    return

def newtopictreesub(mqclient,topic):
    topic='{}/#'.format(topic)
    mqclient.subscribe(topic)
    return

def newtopicpub(mqclient,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    mqclient.publish(topic,data, qos=1,retain=True)
    return

# database section
def getdbconnection(dbhost,dbuser,dbcred,dbinst):
    try:
        thisdbhandle = connect(host=dbhost,user=dbuser,password=dbcred,database=dbinst)
        return thisdbhandle
    except Error as e:
        print(e)

def newcurtempsql(nodeid,curtemp):
    sqlstr='update nodedatatmp set curtemp={} where manodeguid="{}";'.format(curtemp,nodeid)
    return sqlstr

def newsettempsql():
    sqlstr='select manodeguid,settemp from nodedatatmp where settemp IS NOT NULL;'
    return sqlstr

# callback message processing section
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

def getsettemp(nodevars):
    newsql=newsettempsql()
    dbconnect=getdbconnection(nodevars[6],nodevars[7],nodevars[8],nodevars[9])
    if dbconnect:
        with dbconnect.cursor() as cursor:
            cursor.execute(newsql)
            queryresults=cursor.fetchall()
    return queryresults


# set random temp for random MA-Nodes ( replace with SQL calls to settemp column)
def newtemp():
    curtemp=str(round(random.uniform(10.00,35.00),2))
    return curtemp

def getnodeid():
    nodelist=['617985f7-4d40-4b26-9d79-b958fa5bd7c6','5ea489d1-9a6e-4718-a485-d35fd2e526ae','7273b5fe-be3a-4728-b365-567e86f10abc','1f94d059-f3d8-4ad0-b0a3-b12c8f025b60','72621444-8c8c-4cd0-869d-d86380fcdfa8']
    pick=random.randint(0,4)
    return nodelist[pick]



def main():
    nodevars=setvars()
    subclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    subclient.on_message = on_message_write
    # connect to the broker and validate before proceeding
    mqsubstat=newconnect(subclient,nodevars[3],nodevars[4])
    if mqsubstat== 0:
        print("successful connection to mqqt broker")
        #Subscribe to both current temp and diagnostics queues. 
        # Function newtopictreesub uses a wild card to get all nodes publishing
        # to the current temp queue using their MA-Node guid to differntiate sources
        newtopictreesub(subclient,"ct")
        newtopictreesub(subclient,"dd")
        # Loop start puts queue subscription into a backgroun thread
        subclient.loop_start()
        while True: 
            print("go check database for new temperature over-rides")
            # if there is data there create a publishing client and push the data
            # for all nodeid/settemp results:
            records=getsettemp(nodevars)
            for record in records:
                manodeid,setval=record
                #settemp=newtemp()
                #randnode=getnodeid()
                print("encrypt data using {} symetric key".format(manodeid))
                #print("encrypt data using {} symetric key".format(randnode))
                print("Publishing new temperature {} for node {}".format(str(setval),manodeid))
                newtopicpub(subclient,"st",manodeid,str(setval))
            # once all are published disconnect
            time.sleep(30)
            pass


if __name__=="__main__":
    main()
