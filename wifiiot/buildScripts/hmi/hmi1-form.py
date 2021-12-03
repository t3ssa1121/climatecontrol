from flask import Flask, render_template, request
import datetime
# add in form validation 
#from flask_wtf import Form
#from wtforms import TextField

app = Flask(__name__)


@app.route('/')
def status1():
    now = datetime.datetime.now()
    thistime = now.strftime("%Y-%m-%d %H:%M:%S")
    templatedata = {
    'title':'Hey, Move It! default',
    'time':thistime
    }
    return render_template('index.html', **templatedata)


@app.route('/ctrl1', methods=['POST','GET'])
def ctrl1():
    if request.method == 'POST':
        device = request.form['DeviceId']
        direct = request.form['Direction']
        duratn = request.form['Duration']
        # pass these values to a python script?
        

        # For presentation & debugging on control1.html
        templatedata = {
           'title':'Hey, Move It! Control', 
           'DeviceId':device,
           'Direction':direct,
           'Duration':duratn
        }
        #
        #thisresult = request.form
        return render_template("control1.html",**templatedata)



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080,debug=True)
