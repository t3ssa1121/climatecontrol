#!/usr/bin/env python3
#
# Test script to validate python dependancies and database content
# Run this before starting MQTT broker
#
# ----------------------------------------------------------

import sqlite3 sys

# To Do, get database details from environ variables
brokerdb='/opt/storage/controller.db'   # path to persistent database 
manodecount=3  # confirm you have all the nodes in teh design

dbcon = sqlite3.connect(brokerdb)
dbcur = dbcon.cursor
nodelist=[]
for row in dbcur.execute('select * from manodes order by manode-id'):
    nodelist.append(row)

if len(nodelist) == manodecount:
    print("correct node count: {}".format(manodecount))
    dbvalid=True
    print(nodelist[0])
    print(nodelist[manodecount -1])
else:
    print("Incorrect node count or invalid database")

if dbvalid:
    print("automate the boring stuff and start the MQTT broker with the database content")



