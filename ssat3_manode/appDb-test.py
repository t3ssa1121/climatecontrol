#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build  (Dec 12, 2021)
#           Migrating Database functions to seperate module
#                   
# using python native mysql connector, removing the need for mysql client binaries
# on the microservice node.  # https://pypi.org/project/mysql-connector-python/
# 
# Tracking and changing the state of each MA-Node is a functional requirement of the Controller Microservice.
# A database will be used for persistent storage rather than files or class objects because the controller
# service may go offline periodically. The MA-Nodes will continue to run with their last known good programming
# and the occurance of the controller coming back online must not be handled by an approach such as reseting
# all MA-Nodes to a default temperature.
#
# As the application is extended the database may change, decoupling the database interactions from the
# controller program allows those changes to occur without affecting the controller's activity
#
#------------------------------------------------------------------------------------------------------

from mysql.connector import connect, Error


#DBHOST=environ.get('DBHOST')
#DBUSER=environ.get('DBUSER')
#DBPWD=environ.get('DBPWD')
#DBINST=environ.get('DBINST')
# temp standalone testing
DBHOST="10.100.200.3"
DBUSER="lpappuser"
DBPWD="changeme"
DBINST="qtempapp"


# Database connection and query execution functions
def getdbconnection(dbhost,dbuser,dbcred,dbinst):
    try:
        thisdbhandle = connect(host=dbhost,user=dbuser,password=dbcred,database=dbinst)
        return thisdbhandle
    except Error as e:
        print(e)

def getsettemp():
    newsql=newsettempsql()
    dbconnect=getdbconnection(DBHOST,DBUSER,DBPWD,DBINST)
    if dbconnect:
        with dbconnect.cursor() as cursor:
            cursor.execute(newsql)
            queryresults=cursor.fetchall()
    return queryresults

def updatecurtemprecords(recdict):
    dbconnect=getdbconnection(DBHOST,DBUSER,DBPWD,DBINST)
    #confirm connection before generating SQL
    if dbconnect:
        newsql=newcurtempsql(recdict['manodeid'],recdict['curtemp'])
        with dbconnect.cursor() as cursor:
            cursor.execute(newsql)
            dbconnect.commit()
    # to do, check for successful updates. Out of scope due to time contraints, 
    # set temperature changes from users are prioritized over monitoring via web app
    return


# Application specific SQL
def newcurtempsql(nodeid,curtemp):
    sqlstr='update nodedatatmp set curtemp={} where manodeguid="{}";'.format(curtemp,nodeid)
    return sqlstr

def newsettempsql():
    sqlstr='select manodeguid,settemp from nodedatatmp where settemp IS NOT NULL;'
    return sqlstr







