#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build
#                 1, built out data generation functions and queue publishing.
#                    removing load env, need to instantiate using docker run arg
#                 2, adding connection to "st" message queue used for setting temperature
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
# import custom modules
import controlUnit as cu


def setvars():
    # Load node specific data using environment file
    # Must start the container with --env-file 
    #SECRET_KEY=environ.get('SKEY128')
    #NODEID=environ.get('MANID')
    #QID=environ.get('QID')
    #QPWD=environ.get('QPWD')
    #QHOST=environ.get('QHOST')
    #QPORT=environ.get('QPORT')
    SECRET_KEY='abcdefg'
    NODEID='987654'
    QID="nodetester"
    QPWD="changeme"
    QHOST="10.100.200.3"
    QPORT="1883"
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

def on_message_update(mqclient, userdata, msg):
    # when message is recieved on a queue that is subscribed to this callback event fires
    # read the content of the message, call functions based on content
    result=tuple((msg.topic).split("/"))
    if result[0]=="st":
        print("Received new temperature setting for {} : {}".format(result[1],str(msg.payload)))
        settemp=procsettemp(msg)
        if isinstance(settemp,float):
            global newtemp
            newtemp=settemp
    else:
        print("warning undefined topic: {}".format(msg.topic))
        # write to security log       
    return

def procsettemp(msg):
    # Decrypt payload here:

    # double check message is a float value
    try:
        settemp=float((msg.payload).decode("utf-8"))
        return settemp
    except Exception as e:
        print("Invalid payload")
        print(e)
        return

# Climate control temperature assessment
def testnewtemp(st,tsensor):
    # get current temperature
    ct=tsensor.gettemp()[1]
    # compare set temp value with current temp
    if st < (ct + 1.5):
        # cool by 0.2 degrees in this loop
        tsensor.settemp(-0.2)
        heat=False
        cool=True
    elif st> (ct - 1.5):
        # heat by 0.2 degrees in this loop
        tsensor.settemp(0.2)
        heat=True
        cool=False
    else:
        # by default cool by 0.1 degrees
        tsensor.settemp(-0.1)
        #Ensure heating & cooling off
        cool=False
        heat=False
    return [heat,cool]

def sethcstatus(hclist):
    if hclist[0]:
        callforheat(True)
    else:
        callforcool(False)
    if hclist[1]:
        callforcool(True)
    else:
        callforcool(False)
    return

# Climate Control Equipment Actuators
def callforheat(state):
        if state:
            print("Heating Status: Active")
        else:
            print("Heating Status: Inactive")

def callforcool(state):
        if state:
            print("Cooling Status: Active")
        else:
            print("Cooling Status: Inactive")


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

# Simulate a digital thermometer with a python class that tracks temperature changes made through set method
class TempSensor:
    def __init__(self,name):
        #initate a thermometer class with a safe default temperature of 19 degrees Celcius
        self.name = name
        self.curtemp = float(19.0)

    def settemp(self,tempchange):
        # accepts positive or negative floating value to simulate cooling or heating
        self.curtemp = self.curtemp + float(tempchange)
        # debug
        print("temperature changed to {}".format(self.curtemp))
    
    def gettemp(self):
        # naming the instance allows easier tracking of multiple temp sensors
        return[self.name,self.curtemp]



def main():
    nodevars=setvars()
    
    # communication failure mitigations
    comfailurecount=0
    #extendedcomfailure=False
    # Diagnositcs loop control
    monitorcycle=0
    # Instantiate digital thermometer simulation
    #tempsensor1 = TempSensor('MA-Node_0')
    tempsensor1 = cu.TempSensor("MA-Node_lab")
    # get curent temperature in controlled zone and set heating/cooling to off
    tempdata=tempsensor1.gettemp()
    
    cool=False
    heat=False
    #newtemp=float(19.123)  # ToDo,  need a way to read message queue for correct value, MID not enough
    #
    while True:
        # check for new temperature
        subclient=newclient(nodevars[1],nodevars[2],nodevars[3])
        subclient.on_message = on_message_update
        mqconstat=newconnect(subclient,nodevars[4],nodevars[5])
        if mqconstat == 0:
            subclient.loop_start()
            # check for new temperature setting on "st" message queue
            print("checking st/{} queue for new temperature".format(nodevars[1]))
            subresult=newtopicsub(subclient,"st",nodevars[1])
            if subresult[0]==0 and subresult[1]!=0:
                print("new message on set temp queue")
                time.sleep(2)
                #if newtemp == 19.123:
                #    print("no temp set case to be handled")
                hclist=cu.testnewtemp(newtemp,tempsensor1)
                print(hclist)
                #hclist=testnewtemp(newtemp,tempsensor1)
                #sethcstatus[hclist]
                #cu.sethcstatus[hclist]
            else:
            # by default cool by 0.1 degrees
                tempsensor1.settemp(-0.1)
                #Ensure heating & cooling off
                heat=False
                cool=False
                hclist=[heat,cool]
                print(hclist)
                #cu.sethcstatus[hclist]
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
                # every 15-20 minutes collect diagnostics and publish them (change to 20 for prod )
                if monitorcycle >= 12:
                    #diagdata=newdiag(nodevars[1],comfailurecount)
                    diagdata=cu.newdiag(nodevars[1],comfailurecount)
                    newtopicpub(pubclient,"dd",nodevars[1],diagdata)
                    monitorcycle=0
            pubclient.disconnect()
        time.sleep(random.randint(35,48))
        '''
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
            '''

    


if __name__=="__main__":
    main()