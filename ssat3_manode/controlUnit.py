#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build
#               
#   A module to manage all the classes and functions needed for the climate control
#   simulation. A typical heating and cooling unit would have noe or mroe independant 
#   sensors to check the area temperature and logic to determine if the current temperature
#   is within the desired range. When determined to be either too hot, or too cold the
#   appropriate cooling or heating function should be undertaken. 
#   
#   
#    During both heating an cooling cycles the temperature should also be monitored to identify
#    when the heating or cooling action should be returned to the "off state". Once the desired 
#    temperature has been achieved it should be maintained a steady statewithin .5 to 1 degree
#    until a new temperature change is requested by the person managaing the zone or a scheduled
#    temperature change. All such change decions are managed outside of this module.
#    
#    Safety mechanisms must also be in place to enduse maximum and minimum temperatures will not 
#    be exceeded regardless of temperature change input values. Additionally, diagnostic measurements
#    should be taken periodically and reported to the centralized controller. Saftey limits will
#    be hard coded into the module and not exposed as adjustable settings, this simmulates the out
#    of band control often put into systems via physical measures. The diagnostic function will be
#    utilize random number generation combined with system time information and communication
#    issues detected to simulate the interaction of physical and temporal data collected and 
#    communicated with a remote network node providing maintenance monitoring services.
# 
# -------------------------------------------------------------------------------------------------------  

import random, datetime,json

# minimum and maximum temperatures
tempmin=12.0
tempmax=28.5

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


# Function to request new diagnostic data. Requires the ID of the MA-Node so a central monitoring
# application could process messages from a number of different nodes. Use JSON format to simplify
# the use of key-value pairs.
def newdiag(nodeid,comstats):
    # simulation of collect maintenamce information from sensors
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


