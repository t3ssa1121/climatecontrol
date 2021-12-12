#!/usr/bin/env python3
#  Author(s): Doug Leece  
#  Version Notes: 0, initial build  (Dec 12, 2021)
#           Place Encryption Functions into to seperate module
#                   
# using python native Fernet symmetric encryption cryptography, removing the need for additional encyption software to be 
# included in the microservice node. https://cryptography.io/en/latest/fernet/
# 
# 
#
#------------------------------------------------------------------------------------------------------
import csv
from cryptography.fernet import Fernet

# Temporary for testing, define as env for Docker startup
KEYFILE='/var/tmp/manode_keypairs.csv'

# Encryption section
# Create in memory store of encryption keys
def newkeydict(keyfile):
    with open(keyfile, mode='r') as nkcsv:
        csvreader = csv.reader(nkcsv)
        keydict = { rec[0]:rec[1] for rec in csvreader}
    return keydict

def getkeydict():
    #KEYFILE=environ.get('KEYFILE')
    thiskeydict=newkeydict(KEYFILE)
    return thiskeydict

def encrypt_data(keystr,data):
    bytekey=bytes(keystr,'utf-8')
    enchandle=Fernet(bytekey)
    encbytes=enchandle.encrypt(data)
    return encbytes

def decrypt_data(keystr,data):
    bytekey=bytes(keystr,'utf-8')
    enchandle=Fernet(bytekey)
    try:
        decbytes=enchandle.decrypt(data)
        return decbytes
    except Exception as e:
        print("Payload not encrypted with authorized key")
        pass
        return None