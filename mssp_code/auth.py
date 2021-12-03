import flask
#import flask_login
from flask import Blueprint, render_template, redirect, url_for,flash
from flask_login import login_user,current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . models import User
# Need this for the uncontrolled redirects ( unsupported but check it out)
from urllib.parse import urlparse, urljoin
#def is_safe_url(target):
#    ref_url = urlparse(request.host_url)
#    test_url = urlparse(urljoin(request.host_url, target))
#    return test_url.scheme in ('http', 'https') and \
#           ref_url.netloc == test_url.netloc


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login_post():
    email = flask.request.form.get('email')
    passwd = flask.request.form.get('passwd')
    account=User.query.filter_by(email=email).first()
    if not account or not check_password_hash(account.pwd, passwd):
        flash('Account login failed, unknown account or invalid password. Check login details and try again.')
        return redirect(url_for('auth.login'))
    else:
        login_user(account)
        #next = flask.request.args.get('next')
        #if not is_safe_url(next):
        #    return flask.abort(400)
        thiscid=account.id
        # if valid creds then direct to profile.
        print(current_user.is_authenticated)
        return redirect(url_for('main.csprofile', sessioncid = thiscid))
   

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        sessioncid=current_user.get_id()
        account=User.query.filter_by(id=sessioncid).first()
        msg='already authenticated as {}'.format(account.clientname)
        flash(msg)
        return render_template('index.html')
    else:
        return render_template('login.html')


@auth.route('/register')
def register():
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')
    #return 'Logout'