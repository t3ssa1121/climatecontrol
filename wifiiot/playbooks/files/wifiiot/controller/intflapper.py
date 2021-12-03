#!/usr/bin/env python3

import random, time, sys, subprocess, datetime

# define SSID to be active on, otehrwise sleep 30 seconds
PRDSSID='4D2LAB1YYC'


def check_wlan(intname):
    filepath = '/sys/class/net/' + intname + '/operstate'
    # make sure there is a valid interface
    intstate=False
    try:
        with open(filepath) as fh:
            statetest = fh.read()
        if statetest.strip() == 'up':
            intstate = True
        else:
            intstate = False
    except:
        print('no such interface: ' + 'str(intname)' )
        exit(0)
    return intstate


def check_nic():
    niclist = []
    try:
        #catch ifconfig not working or wlan interfaces didn't come up
        nicdatastr=subprocess.check_output(['ifconfig','-a'],universal_newlines=True).split('\n')
        for line in nicdatastr:
            if line.startswith('wlan'):
                nicid = line.split(':')[0]
                niclist.append(nicid)
    except:
        print('not able to enumerate network interfaces, check permissions')
        pass
    return niclist


def check_essid(wlannic):
    iwlist = subprocess.check_output(['iwconfig',wlannic],universal_newlines=True).split('\n')
    for line in iwlist:
        if 'ESSID' in line:
            print('check if prod essid')
            #mean we are up, are we on teh right network?
            if PRDSSID in line:
                intflap(wlannic)
    return


def intflap(thisnic):
    time.sleep(random.randint(45,185))
    print("drop nic for random interval")
    subprocess.call(['ifconfig',thisnic,'down'])
    time.sleep(random.randint(20,105))
    print('and wake up again')
    subprocess.call(['ifconfig',thisnic,'up'])
    time.sleep(random.randint(25,65))
    return
    

def main():
# First check to see if there is a valid wlan interface,
# if it's up check essid, if known prod network jump to flapping function, else sleep and check again
# ToDo if valid but down try ifconfig up

    while True:
        wlannics = check_nic()
        if len(wlannics)>0:
            for nic in wlannics:
                thisnicstate=check_wlan(nic)
                if thisnicstate:
                    print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
                    check_essid(nic)
                else:
                    print('try to start wlan nic')
        time.sleep(30)

# call main
if __name__ == "__main__":
    main()




