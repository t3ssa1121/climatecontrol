from flask import Flask, render_template, request
import paho.mqtt.client as mqtt
import datetime, json, subprocess, platform




# to do Pull from env vars
brkurl = "192.168.59.11"
brkprt = 4321

def gettime():
    now = datetime.datetime.now()
    thistime = now.strftime("%Y-%m-%d %H:%M:%S")
    return thistime

def onlinestat(hostip):
    prm = '-c' if platform.system().lower()=='linux' else '-n' # Windows & linux only
    pcmd = ['ping',prm,'1',hostip]
    return subprocess.call(pcmd)==0

def readhosts(filename):
    hostdict= dict()
    with open(filename) as fh:
        hostdata = fh.readlines()
    for row in hostdata:
        hostname,hostip =row.split(',')
        hostdict[hostname]=hostip
    return hostdict

def hoststat(hostdict):
    hostonline = dict()
    for host in hostdict:
        stat = onlinestat(hostdict[host])
        if stat:
            hostonline[host]='Green'
        else:
            hostonline[host]='Red'
    return hostonline


def pubmsg(opdir,optime,opdevice):
    ctrldict = dict()
    ctrldict['direction']=opdir
    ctrldict['duration']=optime
    ctrldict['device']=opdevice
    ctrljson = json.dumps(ctrldict)
    return ctrljson



# to-do import dropdown values for devices, pass as an array to index.html templge

app = Flask(__name__)


@app.route('/')
def status1():
    devonline = hoststat(readhosts('devices.txt'))

    templatedata = {
    'title':'Hey, Move It! default',
    'time':gettime(),
    'onlinedata': devonline
    }
    return render_template('index.html', **templatedata)


@app.route('/ctrl1', methods=['POST','GET'])


def ctrl1():
    if request.method == 'POST':
        #Collect the form values
        device = request.form['DeviceId']
        direct = request.form['Direction']
        duratn = request.form['Duration']
        thismsg = pubmsg(direct,duratn,device)
        # Push the instructions to the broker
        try:
            client = mqtt.Client()
            client.connect(brkurl,brkprt)
            client.publish(topic="fieldsite/ctrl_motor",payload=thismsg,qos=1, retain=False)

        except Exception as err:
            print('Failed to connect to broker server')
            print(err)

        # Presentation of commands, good for debug
        templatedata = {
           'title':'Hey, Move It! Control', 
           'DeviceId':device,
           'Direction':direct,
           'Duration':duratn
        }
        return render_template("control1.html",**templatedata)
    

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)
