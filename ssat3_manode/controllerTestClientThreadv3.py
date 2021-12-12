#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build  (Dec 8, 2021)
#                   
#  Using the python paho client https://www.eclipse.org/paho/index.php?page=clients/python/index.php to
#  limit the amount of additional software to be installed on the microservice container.
#
#  On startup the conntroller program will read node ID and symetric key values from file and
#  store this in an in memory dictionary. In a more resilent production system this ID and encryption
#  key date would be retrieved from a key management service avaliable from the cloud providerThis will eliminate the accidental exposure of 
#  key values in a code repository EG https://www.vaultproject.io/.
#
#  During operation the controller subscribes to the top level current temperature & diagnositics topics,
#  using MA-Node GUID based sub topics to ensure the correct database records are updated.
#  
#  On frequent intervals, (currently 30 seconds but configurable in the code), the controller retrieves
#  all user set temperature changes from a database, encrypts with the node's specific symetric key,
#  and publishes this encrypted payload to the specific set temperature topic used by that MA-Node.
#  The MA-Node will only initiate temperature changes for messages that can be properly decrypted, providing
#  a very high degree of assurance that the change instruction came from the authorized controller and not
#  an MQTT message forged and submitted by an adversary.
#   
#  Note: Encrypting current temperature values reported by the nodes is a secondary priority
#  since there is no ability to change MA-Node operations from this data and it would 
#  not typically be considered private data. This functionality is currently not implemented.


import  paho.mqtt.client as paho
import json, sys, datetime,random,time, csv
from os import environ
from os import path
from mysql.connector import connect, Error
# import custom modules
import appDb as adb
import appEnc as aenc

# Simulating the minimum and maximum temperature values that would be set by the system owner,
# these would typically be retrieved from a database that was updated via RBAC controled application
sotempmin=14.99
sotempmax=25.99



def setvars():
    #CLIENTID=environ.get('CLIENTID')
    #QID=environ.get('QID')
    #QPWD=environ.get('QPWD')
    #QHOST=environ.get('QHOST')
    #QPORT=environ.get('QPORT')
    # temp standalone testing
    CLIENTID='123456'
    QID="nodetester"
    QPWD="changeme"
    QHOST="10.100.200.3"
    QPORT="1883"
    
    return[CLIENTID,QID,QPWD,QHOST,QPORT]

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

# Function newtopictreesub uses a wild card to get all nodes publishing to the current temperature MQTT topic.
# The topic is a tree structure using the unique GUID for each MA-Node differntiate the
# values provided for each system. This is a key requirement because each MA-Node has a unique
# symetric encryption key, knowing the MA-Node that supplied the data allows the correct key 
# to be selected during the decryption proccess.
def newtopictreesub(mqclient,topic):
    topic='{}/#'.format(topic)
    mqclient.subscribe(topic)
    return

def newtopicpub(mqclient,topic,nodeid,data):
    topic='{}/{}'.format(topic,nodeid)
    mqclient.publish(topic,data, qos=1,retain=True)
    return

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
    adb.updatecurtemprecords(recdict)
    return

def updatediaglog(logfile,recjson):
    with open(logfile, 'a') as jsonfh:
         jsonfh.write(recjson)
         jsonfh.write('\n')
    return

def getenckey(nodeid,keydict):
    nodekey = keydict[nodeid]
    return nodekey

# Function to encrypt the node specific set temperature value with the node's symmetric key
def enc_settemp(tempfloat,key):
    tempbytes=bytes(str(tempfloat))
    print(tempbytes)
    print(type(tempbytes))
    return


def main():
    nodevars=setvars()
    # Retrieve encryption keys for each node
    thiskeydict = aenc.getkeydict()
    subclient=newclient(nodevars[0],nodevars[1],nodevars[2])
    subclient.on_message = on_message_write
    # connect to the broker and validate before proceeding
    mqsubstat=newconnect(subclient,nodevars[3],nodevars[4])
    if mqsubstat== 0:
        print("successful connection to mqqt broker")
        #Subscribe to both current temp and diagnostics queues. 
        newtopictreesub(subclient,"ct")
        newtopictreesub(subclient,"dd")
        # Loop start puts queue subscription into a background thread
        subclient.loop_start()
        while True: 
            print("go check database for new temperature over-rides")
            # if there is data there create a publishing client,encrypt with the node's key before publishing
            records=adb.getsettemp()
            for record in records:
                manodeid,setval=record
                thiskey=getenckey(manodeid,thiskeydict)
                print("encrypt setval data {} using {} symetric key {}".format(setval,manodeid, thiskey))
                enc_settemp(setval,thiskey)
                print("Publishing new temperature {} for node {}".format(str(setval),manodeid))
                newtopicpub(subclient,"encst",manodeid,str(setval))
            
            time.sleep(30)
            pass


if __name__=="__main__":
    main()
