#!/usr/bin/env python
import os, sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv

 
# Database setup --------------------------------------------------------
# Extract creds from environment variables
def getconnectiondata():
    condatalist=[]
    nidsdb=os.environ['dbinstance']
    username=os.environ['dbuser']
    cred=os.environ['dbcred']
    host=os.environ['dbhost']
    if not nidsdb:
        print("Missing database connection info: database instance name")
    else:
        condatalist.append(nidsdb)
    if not username:
        print("Missing database connection info: database user name")
    else:
        condatalist.append(username)
    if not cred:
        print("Missing database connection info: database credential")
    else:
        condatalist.append(cred)
    if not host:
        print("Missing database connection info: database host information")
    else:
        condatalist.append(host)
    if len(condatalist) !=4:
        print("missing database connection info, please correct")
        exit(1)
    else:
        return condatalist
    return False

def newdbengine(connlist):
    # adjust based on order in list
    user=connlist[1]
    pwd=connlist[2]
    host=connlist[3]
    dbinst=connlist[0]
    #connection string
    constring="mysql+pymysql://{}:{}@{}:3306/{}".format(user,pwd,host,dbinst)
    thisengine = create_engine(constring)
    return thisengine

def newdburi(connlist):
    # adjust based on order in list
    user=connlist[1]
    pwd=connlist[2]
    host=connlist[3]
    dbinst=connlist[0]
    #connection string
    dburi="mysql://{}:{}@{}:3306/{}".format(user,pwd,host,dbinst)
    return dburi



def create_app(dburi):
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_DATABASE_URI']=dburi




    return app

if __name__ == "__main__":
    connlist=getconnectiondata()
    dburi=newdburi(connlist)
    # simple test first
    db = SQLAlchemy()
    create_app(dburi)

    
