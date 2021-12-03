from flask import Blueprint,render_template, redirect,url_for, request, flash, Markup
from flask_login import  login_required, current_user
from werkzeug.security import generate_password_hash
from . import db
from . models import User
import os

main = Blueprint('main', __name__)


def getclientpath(cid,arcid):
    if arcid == 14:
        clientpath = "/opt/balam/clients/{}/datamgmt/14".format(cid)
    elif arcid == 30:
        clientpath = "/opt/balam/clients/{}/datamgmt/30".format(cid)
    elif arcid == 90:
        clientpath = "/opt/balam/clients/{}/datamgmt/90".format(cid)
    else:
        clientpath = "/opt/balam/clients/{}/datamgmt/99".format(cid)
    return clientpath


@main.route('/')
def index():
    print(current_user.is_authenticated)
    return render_template('index.html')

# If no customer ID then redirect to login page
# Current bug? user you can guess customer ID?
#@main.route('/customer', defaults={'sessioncid': None})
#@main.route('/customer/<sessioncid>')
@main.route('/customer')
@login_required
def csprofile():
    #print(current_user.is_authenticated)
    #if current_user.is_authenticated:
    sessioncid=current_user.get_id()
    account=User.query.filter_by(id=sessioncid).first()
    return render_template('customer.html', scid=sessioncid,scname=account.clientname )
    #else:
    #    return render_template('customer.html')

@main.route('/data-management')
@login_required
def buprofile():
    #print(current_user.is_authenticated)
    #if current_user.is_authenticated:
    sessioncid=current_user.get_id()
    account=User.query.filter_by(id=sessioncid).first()
    return render_template('datamgmt.html', scid=sessioncid,scname=account.clientname )
    


@main.route('/sensor/<sessioncid>')
def sensorprofile(sessioncid):
    return render_template('sensor.html')

@main.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    clientid = request.form.get('clientid')
    password = request.form.get('password')
    account= User.query.filter_by(email=email).first()
    if account:
        flash('Sorry, the email address {} appears to be in use'.format(email))
        return redirect(url_for('auth.register'))
    account= User.query.filter_by(id=clientid).first()
    if not account:
        msg=Markup('Sorry, the account identifier does not appear to preregistered, double check you have input the 5 digit code correctly.<br/> If you are still encountering issues please contact Balam customer support: <br/> 1-888-BALAM27 (1-888-225-2627)')
        flash(msg)
        return redirect(url_for('auth.register'))
        #return '<h1> Sorry, the account identifier does not appear to preregistered, double check you have input the 6 digit code correctly</h1><h2>If you are still encountering issues please contact Balam customer support at 1-888-BALAM27 (1-888-225-2627)</h2>'
    if account.email:
        msg=Markup('Sorry, the account identifier {} is currently associated with the email {}'.format(account.id, account.email))
        flash(msg)
        return redirect(url_for('auth.register'))
        #return '<h1> Sorry, the account identifier {} is currently associated with the email {}</h1>'.format(account.id, account.email)
    else:
        # Do the SQL update here
        pwdstr = generate_password_hash(password)
        account.email= email
        account.pwd = pwdstr 
        db.session.commit()
        #User.query.filter_by(id=clientid).update(dict(email=email,pwd=pwdstr))
        return render_template('signup.html',id=clientid,email=email,clientname=account.clientname)
        #return '<h1> Input cid: {}, email: {}, pwd: {} for company {}'.format(clientid,email,password,account.clientname)

#@main.route('/data-access')
#@login_required
#def dm14():
#    sessioncid=current_user.get_id()
#    account=User.query.filter_by(id=sessioncid).first()
#    # list directory content to make URLs
#    cpath = getclientpath(sessioncid,14)
#    files=os.listdir(cpath)
#    urllist=[]
#    for file in files:
#        url="https://datahub.balam.ca/{}/dm14/{}".format(sessioncid,file)
#        urllist.append(url)
#    # To do, get second list of file names to make things prettier on the other end
#    return render_template('dataaccess.html', scid=sessioncid,scname=account.clientname,filelinklist=urllist)