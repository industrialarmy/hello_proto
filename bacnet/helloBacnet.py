# -*- coding: utf-8 -*-
import sys
from socket import *
 
HST     = sys.argv[1]
port    = 47808 # [bacnet] Default port: 47808
tramaX  = {}
 
_bacnet_obj_description = { 
                        0: "Vendor Name",  
                        1: "Instance ID",  
                        2: "Firmware",     
                        3: "Apps Software",
                        4: "Object Name",  
                        5: "Model Name",   
                        6: "Description",
                        7: "Location"
}
 
hder = "\x81\x0a\x00\x11\x01\x04\x00\x05\x01\x0c\x0c\x02\x3f\xff\xff\x19"
 
tramaX[0]  = hder+"\x79"
tramaX[1]  = hder+"\x4b"
tramaX[2]  = hder+"\x2C"
tramaX[3]  = hder+"\x0C"
tramaX[4]  = hder+"\x4D"
tramaX[5]  = hder+"\x46"
tramaX[6]  = hder+"\x1c"
tramaX[7]  = hder+"\x3a"
 
def BACnet(nObj):
    objBnet = ''
    s = socket(AF_INET,SOCK_DGRAM)
    s.connect((HST,int(port)))
 
    sndFrm = tramaX[nObj]
    s.send(sndFrm)
    dump = s.recv(2048)
 
    if (nObj == 1): #
        objBnet = int(str(dump)[19:-1].encode("hex"),16)
    else:
        objBnet = str(dump)[19:-1]
    s.close()
    return objBnet
 
totFRm = len(tramaX)   
print "\n"
for objN in range(0,totFRm):
    strBacnet   = str(BACnet(int(objN)))
    desc        =_bacnet_obj_description[objN]
    print " [+] "+desc+":  \t    "+strBacnet
 
print "\n" 
