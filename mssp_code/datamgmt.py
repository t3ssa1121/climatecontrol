from flask import Blueprint,render_template, redirect,url_for, request, flash, Markup
from flask_login import  login_required, current_user
from werkzeug.security import generate_password_hash
from . import db
from . models import User
# directory listing functions
import os,time


datamgmt = Blueprint('datamgmt', __name__)

def getclientpath(cid,arcid):
    if arcid == 14:
        clientpath = "/opt/balam/clients/{}/dm/14".format(cid)
    elif arcid == 30:
        clientpath = "/opt/balam/clients/{}/dm/30".format(cid)
    elif arcid == 90:
        clientpath = "/opt/balam/clients/{}/dm/90".format(cid)
    else:
        clientpath = "/opt/balam/clients/{}/dm/99".format(cid)
    return clientpath

def getfiletime(fullpath):
    ftime=os.path.getmtime(fullpath)
    datatime=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ftime))
    return datatime




@datamgmt.route('/data-access/dm14')
@login_required
def dm14():
    sessioncid=current_user.get_id()
    account=User.query.filter_by(id=sessioncid).first()
    ## list directory content to make URLs
    cpath = getclientpath(sessioncid,14)
    files=os.listdir(cpath)
    filedata=[]
    for file in files:
        fpath="{}/{}".format(cpath,file)
        datatime=getfiletime(fpath)
        url="https://datahub.balam.ca/{}/dm/14/{}".format(sessioncid,file)
        ftuple=(file,datatime,url)
        filedata.append(ftuple)
    drmsg = "Current - 14 days"
    return render_template('dataaccess.html', scid=sessioncid,scname=account.clientname, filetuple=filedata, pgmsg=drmsg)


@datamgmt.route('/data-access/dm/30')
@login_required
def dm30():
    sessioncid=current_user.get_id()
    account=User.query.filter_by(id=sessioncid).first()
    ## list directory content to make URLs
    cpath = getclientpath(sessioncid,30)
    files=os.listdir(cpath)
    filedata=[]
    for file in files:
        fpath="{}/{}".format(cpath,file)
        datatime=getfiletime(fpath)
        url="https://datahub.balam.ca/{}/dm/30/{}".format(sessioncid,file)
        ftuple=(file,datatime,url)
        filedata.append(ftuple)
    drmsg = "15 to 30 days"
    return render_template('dataaccess.html', scid=sessioncid,scname=account.clientname, filetuple=filedata, pgmsg=drmsg)


@datamgmt.route('/data-access/dm90')
@login_required
def dm90():
    sessioncid=current_user.get_id()
    account=User.query.filter_by(id=sessioncid).first()
    ## list directory content to make URLs
    cpath = getclientpath(sessioncid,90)
    files=os.listdir(cpath)
    filedata=[]
    for file in files:
        fpath="{}/{}".format(cpath,file)
        datatime=getfiletime(fpath)
        url="https://datahub.balam.ca/{}/dm/90/{}".format(sessioncid,file)
        ftuple=(file,datatime,url)
        filedata.append(ftuple)
    drmsg = "30 to 90 days"
    return render_template('dataaccess.html', scid=sessioncid,scname=account.clientname, filetuple=filedata, pgmsg=drmsg)


@datamgmt.route('/data-access/dm99')
@login_required
def dm99():
    sessioncid=current_user.get_id()
    account=User.query.filter_by(id=sessioncid).first()
    ## list directory content to make URLs
    cpath = getclientpath(sessioncid,99)
    files=os.listdir(cpath)
    filedata=[]
    for file in files:
        fpath="{}/{}".format(cpath,file)
        datatime=getfiletime(fpath)
        url="https://datahub.balam.ca/{}/dm/99/{}".format(sessioncid,file)
        ftuple=(file,datatime,url)
        filedata.append(ftuple)
    drmsg = "archives 91 days plus"
    return render_template('dataaccess.html', scid=sessioncid,scname=account.clientname, filetuple=filedata, pgmsg=drmsg)