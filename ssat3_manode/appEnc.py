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
from os import environ

# Temporary for testing, define as env for Docker startup
#KEYFILE='/var/tmp/manode_keypairs.csv'

# Encryption section
# Create in memory store of encryption keys
def newkeydict(keyfile):
    with open(keyfile, mode='r') as nkcsv:
        csvreader = csv.reader(nkcsv)
        keydict = { rec[0]:rec[1] for rec in csvreader}
    #keydict={
    #    "5ea489d1-9a6e-4718-a485-d35fd2e526ae":"ZB0_jL1BTPeTTaoQbw3tbXAiswHVdQQf3Yq2r2JeEbA=",
    #    "617985f7-4d40-4b26-9d79-b958fa5bd7c6":"neUmjjOXook1mruyFuOAgzMSy6CH91A3rREUuGwAvig=",
    #    "7273b5fe-be3a-4728-b365-567e86f10abc":"xOgiEQ12ASfvQrNgEOsHvOIlXv18FL_H9CDePT6PEcE=",
    #    "1f94d059-f3d8-4ad0-b0a3-b12c8f025b60":"Q9_ZiOvLp-kbJJdyC2ClkNcf5tC1DHyYDjQh2xbC-ww=",
    #    "72621444-8c8c-4cd0-869d-d86380fcdfa8":"Bv8WxO9BiDEjER70QosDSTG6-Pt4JoEzceoqjlZ3x5U=",
    #    "987654":"xB0O3-6KbNrPaLFJGBr2Rdpm9rVVz8K7trDVk-h6cQs="    }
    return keydict

def getkeydict():
    KEYFILE=environ.get('KEYFILE')
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