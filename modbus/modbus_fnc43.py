# -*- coding: utf-8 -*-
import socket
import sys
 
mbIP    = sys.argv[1]
mbPort  = sys.argv[2]
SID     = sys.argv[3]
 
class Colors:
    BLUE        = '\033[94m'
    GREEN       = '\033[32m'
    RED         = '\033[0;31m'
    DEFAULT     = '\033[0m'
    ORANGE      = '\033[33m'
    WHITE       = '\033[97m'
    BOLD        = '\033[1m'
    BR_COLOUR   = '\033[1;37;40m'
 
_modbus_obj_description = { 
                        0: "VendorName",   
                        1: "ProductCode",  
                        #2: "MajorMinorRevision",
                        2: "Revision",     
                        3: "VendorUrl",
                        4: "ProductName",  
                        5: "ModelName",
                        #6: "UserApplicationName",
                        6: "User App Name",
                        7: "Reserved", 
                        8: "Reserved", 
                        9: "Reserved", 
                        10: "Reserved",
                        128: "Private objects",
                        255: "Private objects"
                        }
# ------------------------------------------------------------------------------ #
 
 
def getDevInfo(mvIdentification):
 
    aframe = mvIdentification.encode("hex")
 
    print "\n"
    print  Colors.BLUE+' [+] Host: \t\t' +Colors.RED+mbIP+Colors.DEFAULT
    print  Colors.BLUE+' [+] Port: \t\t' +Colors.ORANGE+str(mbPort)+Colors.DEFAULT
    print  Colors.BLUE+' [+] Slave ID: \t\t' +Colors.RED+aframe[12:14]+Colors.DEFAULT
 
    respCode    = aframe[14:16]
    totalObjs   = aframe[26:28]
    firstObj    = 28
 
    try:
        try:
            objTot = aframe[26:28]
            nObjeto = int(objTot,16)
        except:
            #objTot = '0'
            nObjeto = int('0',10)
 
        print Colors.BLUE+' [+] TotalObj: \t\t'+Colors.RED+str(nObjeto)+"\n"+Colors.DEFAULT
        pInicial = 28
 
        for i in xrange(0,nObjeto):
            pInicial+=4
            longitud = aframe[pInicial-2:pInicial]
            longitud = int(longitud,16)
                             
            valueStr = aframe[pInicial:pInicial+longitud *2 ]
            objVal   = valueStr.decode("hex")
 
            try:
                obj_nm =_modbus_obj_description[i]
            except:
                obj_nm ='objName X'
 
            print Colors.BOLD+ " [*]  "+Colors.GREEN+ obj_nm +': \t'+Colors.ORANGE+objVal+Colors.DEFAULT
            pInicial+=longitud*2
     
    except Exception, e:
        print  Colors.BR_COLOUR+Colors.RED+'\n [!] no device info' + Colors.DEFAULT
        print e
     
    print "\n"
 
# ------------------------------------------------------------------------------ #
func_code   = '2b'  # Device Identification
meiType     = '0e'  # MODBUS Encapsulated Interface - 0e / 0d
read_code   = '03'  # 01 / 02 / 03 / 04 
obj_id      = '00' 

# --MBAP 7 Bytes --------------------------------------------------------  #
# Return a string with the modbus header
def create_header_modbus(length,unit_id):
    trans_id = "4462"           # random; id de transaccion 
    proto_id = "0000"           # campo reservado
    protoLen = length.zfill(4)  # Longitud
    unit_id = unit_id           # Slave ID

    return trans_id + proto_id + protoLen + unit_id.zfill(2)

def fn43():
    modbusRequest =     create_header_modbus('5',SID)
    modbusRequest +=    func_code
    modbusRequest +=    meiType
    modbusRequest +=    read_code
    modbusRequest +=    obj_id


    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((mbIP,int(mbPort)))
 
    #client.send( "\x44\x62\x00\x00\x00\x05"+SID+"\x2b\x0e\x03\x00")
    client.send( modbusRequest.decode("hex") )
    modResponse = client.recv(2048)
 
    client.close()
    return modResponse
 
 
devInfo = fn43()
getDevInfo(devInfo)