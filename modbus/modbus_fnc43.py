# -*- coding: utf-8 -*-
import socket
import argparse
import binascii

parser = argparse.ArgumentParser()
parser.add_argument("host", help="Destination host", type=str)
parser.add_argument("-port", help="Destination port", required=False, type=int, default=502)
parser.add_argument("-slaveid", help="SlaveID", required=False, type=str, default="00")
args = parser.parse_args()

host = args.host
port = args.port
host = args.host
sid = args.slaveid

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[32m'
    RED = '\033[0;31m'
    DEFAULT = '\033[0m'
    ORANGE = '\033[33m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    BR_COLOUR = '\033[1;37;40m'

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

def pretty_print(color, key, color2, value):
    print ("{} [+] {}: \t\t{}{}{}".format(color,key,color2,value,Colors.DEFAULT))


def getDevInfo(mv_identification):
    frame = binascii.hexlify(mv_identification).decode()
    sid = str(frame[12:14])

    print("\n")
    pretty_print(Colors.BLUE, "Host", Colors.RED, host)
    pretty_print(Colors.BLUE, "Port", Colors.ORANGE, str(port))
    pretty_print(Colors.BLUE, "Slave ID", Colors.RED, sid)

    # resp_code = frame[14:16]
    # total_objects = frame[26:28]
    # first_object = 28

    try:
        try:
            obj_total = frame[26:28]
            cant_objetos = int(obj_total,16)
        except:
            cant_objetos = int('0',10)

        pretty_print(Colors.BLUE, "TotObj", Colors.RED, str(cant_objetos)+"\n")

        p_inicial = 28
        for i in range(0, cant_objetos):
            p_inicial+=4
            longitud = frame[p_inicial-2:p_inicial]
            longitud = int(longitud, 16)

            valueStr = frame[p_inicial:p_inicial+longitud *2]
            objVal = binascii.unhexlify(valueStr).decode()

            try:
                obj_nm =_modbus_obj_description[i]
            except:
                obj_nm ='objName X'

            print(Colors.BOLD+ " [*]  "+Colors.GREEN+ obj_nm +': \t'+Colors.ORANGE+str(objVal)+Colors.DEFAULT)
            p_inicial += longitud*2

    except Exception as e:
        print(Colors.BR_COLOUR+Colors.RED+'\n [!] no device info' + Colors.DEFAULT)
        print(e)

    print ("\n")

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
    proto_len = length.zfill(4)  # Longitud
    unit_id = unit_id           # Slave ID

    return trans_id + proto_id + proto_len + unit_id.zfill(2)

def fn43():
    modbus_request = create_header_modbus('5',sid)
    modbus_request += func_code
    modbus_request += meiType
    modbus_request += read_code
    modbus_request += obj_id

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host,int(port)))

    client.send(binascii.unhexlify(modbus_request)+b"\n")
    modResponse = client.recv(2048)
    client.close()
    return modResponse

devInfo = fn43()
getDevInfo(devInfo)