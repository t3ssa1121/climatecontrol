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
        print("Received current temp from {} : {}".format(result[1],str(msg.payload)))
        #processcurtemp(result[1],msg)
    elif result[0]=="dd":
        print("Received diagnostics from {} : {}".format(result[1],str(msg.payload)))
        #processdiagnotics(result[1],msg)
    else:
        print("warning undefined topic: {}".format(msg.topic))
        # write to security log       
    return

def newtopictreesub(mqclient,topic):
    topic='{}/#'.format(topic)
    mqclient.subscribe(topic)
    return


def main():
    nodevars=setvars()
    subclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    #Subscribe to both current temp and diagnostics queues. 
    # Function newtopictreesub uses a wild card to get all nodes publishing
    # to the current temp queue using their MA-Node guid to differntiate sources
    newtopictreesub(subclient,"ct")
    newtopictreesub(subclient,"dd")
    # connect to the broker and validate before proceeding
    mqsubstat=newconnect(subclient,nodevars[3],nodevars[4])
    if mqsubstat== 0:
        print("successful connection to mqqt broker")
        # Loop start puts queue subscription into a backgroun thread
        subclient.loop_start()
        while True:
            print("If I were a real publisher I could push some code")
            print("go check database for new temperature over-rides")
            time.sleep(30)
            pass





if __name__=="__main__":
