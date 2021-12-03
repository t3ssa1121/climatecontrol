#!/usr/bin/env python3
import paho.mqtt.client as mqtt

# Config dest IP and port
brkrurl = '192.168.59.11'
brkrport = 4321

client = mqtt.Client()
client.connect(brkrurl,brkrport)

client.publish(topic="fieldsite/ctrl_beacon",payload="22:13:01:33.429493251",qos=1, retain=False)

