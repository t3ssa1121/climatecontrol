#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time, json

# Setting as BCM because of sparkfun breakout
GPIO.setmode(GPIO.BCM)
# set as normal if using direct pins 
#GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#Using Pin 18 as chaos
# 17 forward / postive
# 17 reverse / negative 
GPIO.setup(18, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
# set everything to off first
GPIO.output(18, GPIO.LOW)
GPIO.output(17, GPIO.LOW)
GPIO.output(16, GPIO.LOW)


#to do, pull from env vars
# Config dest IP and port
brkrurl = '192.168.59.11'
brkrport = 4321

# data input validation section
def check_dur(uknval):
    try:
        testval = float(uknval)
    except:
        print("Invalid duration data")
        return False
    if (testval < 15.0) and (testval > 0.0):
        return True
    else:
        print("Invalid duration value")
        return False

def check_json_dict(uknjson):
    try:
        testoper=uknjson['direction']
    except:
        print("Invalid motor control data")
        return False
    try:
        testoper=uknjson['duration']
    except:
        print("Invalid motor control data")
        return False
    else:
        return True




# create client instance and functionality
def on_connect(client, userdata, flags, rc):
    print("Connected With Result Code " + (rc))
    return


def on_message_from_beacon(client, userdata, message):
    thismsg = message.payload.decode()
    print("Message Recieved from beacon: "+thismsg)
    # Beacon bug
    if (thismsg.find('13') != -1):
        # to do, test if this is a value that can be turned into a float or make 0.0
        rpiio(thismsg[10:14])
        return


def on_message_from_motor(client, userdata, message):
    thismsg = message.payload.decode()
    print("Message Recieved from motor: "+thismsg)
    # ensure properly formed json
    try:
        msgdict = json.loads(thismsg)
        validdict = check_json_dict(msgdict)    
    except:
        return
        #thismsg = '{"direction":"dde", "duration":"0.0"}'
        #msgdict = json.loads(thismsg)
    
    if validdict:
        if msgdict['direction'] in 'fwd':
            try:
                validduration = check_dur(msgdict['duration'])
            except:
                print("Invalid duration field")
                return
            if validduration:
                rpiio1(msgdict['duration'])    
        elif msgdict['direction'] in 'rev' :
            try:
                validduration = check_dur(msgdict['duration'])
            except:
                print("Invalid duration field")
                return
            if validduration:
                rpiio2(msgdict['duration'])
        else:
            print("Invalid motor command")
        return


def rpiio1(intval):
    print("power motor fwd for this many seconds: " + intval)
    GPIO.output(17, GPIO.HIGH)
    time.sleep(float(intval))
    GPIO.output(17, GPIO.LOW)
    return


def rpiio2(intval):
    print("power motor rev for this many seconds: " + intval)
    GPIO.output(16, GPIO.HIGH)
    time.sleep(float(intval))
    GPIO.output(16, GPIO.LOW)
    return


def rpiio(intval):
    print("power motor for this many seconds: " + intval)
    GPIO.output(18, GPIO.HIGH)
    time.sleep(float(intval))
    GPIO.output(18, GPIO.LOW)
    return


# to do,  add more client settings like ID  
client = mqtt.Client()
client.on_connect = on_connect
#To Process Every Other Message
client.on_message = on_message_from_beacon
client.connect(brkrurl, brkrport)
client.subscribe("fieldsite/ctrl_beacon", qos=1)
client.subscribe("fieldsite/ctrl_motor", qos=1)
client.message_callback_add("fieldsite/ctrl_beacon", on_message_from_beacon)
client.message_callback_add("fieldsite/ctrl_motor", on_message_from_motor)
# start in screen or boot up script
client.loop_forever()
