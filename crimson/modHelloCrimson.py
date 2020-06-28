# -*- coding: utf-8 -*-
import sys
import socket
 
HST     = sys.argv[1]
port    = 789 # [Crimson] Default port: 789
tramaX  = {}
 
_crimson_obj_description = { 
                        0: "Vendor Name",  
                        1: "Device model", 
}
#                length ( 2bytes)
#                 / |
tramaX[0]  = "\x00\x04\x01\x2b\x1b\x00"
tramaX[1]  = "\x00\x04\x01\x2a\x1a\x00"
 
 
def crimson(nObj):
    objBnet = ''
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HST,int(port)))
 
    sndFrm = tramaX[nObj]
    s.send(sndFrm)
     
    dump = s.recv(2048)
 
    if (nObj == 1): #
        objCrms = str(dump)
    else:
        objCrms = str(dump)
    s.close()
    return objCrms
 
totFRm = len(tramaX)   
print "\n"


def reqCrm():
    _response_crimson = []
    for objN in range(0,totFRm):
        crimsonDesc     = str(crimson(int(objN)))
        desc            =_crimson_obj_description[objN]
        rsp = desc+": "+crimsonDesc[6:]
        _response_crimson.append(str(rsp)[:-1])
    
    return _response_crimson

print reqCrm()