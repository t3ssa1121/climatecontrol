#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build
# 
#  using paho client https://www.eclipse.org/paho/index.php?page=clients/python/index.php
#
#  Test client reads node ID and symetric key from file
#  Initiates connections to each function topic using heirarchical structure
#  Generates random payloads for each function
#  set enc=False to disable encryption
#  Run in 15 second loop to allow logic testing for controller
#  
############################################################

import  paho.mqtt.client as paho
import json, sys, datetime,random


print("deps met")
