# @Author: Ezequiel Fernandez
# @Author: Juan Escobar @itsecurityco

import binascii
import socket
import sys

try:
    from colorama import Fore, Back, init
    init()
except ImportError:
    print("Colorama is not installed: {cmd}".format(cmd = "sudo pip3 install colorama"))
    exit(1)

host = sys.argv[1]
port = 502
bufsize = 2048
payload = (
    "\x44\x62" # Transaction Identifier
    "\x00\x00" # Protocol Identifier
    "\x00\x05" # Length
    "\x00"     # Unit Identifier
    "\x2b"     # .010 1011 = Function Code: Encapsulated Interface Transport (43)
    "\x0e"     # MEI type: Read Device Identification (14)
    "\x03"     # Read Device ID: Extended Device Identification (3)
    "\x00"     # Object ID: VendorName (0)
)

object_name = { 
    0: "VendorName",
    1: "ProductCode",
    2: "MajorMinorRevision",
    3: "VendorUrl",
    4: "ProductName",
    5: "ModelName",
    6: "UserAppName",
    7: "Reserved",
    8: "Reserved",
    9: "Reserved",
    10: "Reserved",
    128: "PrivateObjects",
    255: "PrivateObjects"
}

# Modbus/TCP Response Bytes
mbtcp = {
    "trans_id":         { "start":  0, "bytes": 2, "length": 4, "end":  4 },
    "prot_id":          { "start":  4, "bytes": 2, "length": 4, "end":  8 },
    "len":              { "start":  8, "bytes": 2, "length": 4, "end": 12 },
    "unit_id":          { "start": 12, "bytes": 1, "length": 2, "end": 14 },
    "func_code":        { "start": 14, "bytes": 1, "length": 2, "end": 16 },
    "mei":              { "start": 16, "bytes": 1, "length": 2, "end": 18 },
    "read_device_id":   { "start": 18, "bytes": 1, "length": 2, "end": 20 },
    "conformity_level": { "start": 20, "bytes": 1, "length": 2, "end": 22 },
    "more_follows":     { "start": 22, "bytes": 1, "length": 2, "end": 24 },
    "next_object_id":   { "start": 24, "bytes": 1, "length": 2, "end": 26 },
    "num_objects":      { "start": 26, "bytes": 1, "length": 2, "end": 28 },
    "object_id":        { "start": 28, "bytes": 1, "length": 2, "end": 30 },
    "objects_len":      { "start": 30, "bytes": 1, "length": 2, "end": 32 },
    "object_str_value": { "start": 32, "bytes": None, "length": None, "end": None }
}

def dec(hex):
    return int(hex, 16)

def parse_response(data):
    data = binascii.hexlify(data)
    unit_id = data[mbtcp["unit_id"]["start"]:mbtcp["unit_id"]["end"]]
    
    print("")
    print("{} [+] Host:\t\t{}{}{}".format(Fore.BLUE, Fore.RED, host, Fore.RESET))
    print("{} [+] Port:\t\t{}{}{}".format(Fore.BLUE, Fore.RED, str(port), Fore.RESET))
    print("{} [+] Unit Identifier:\t{}{}{}".format(Fore.BLUE, Fore.YELLOW, unit_id.decode("utf-8"), Fore.RESET))
 
    try:
        num_objects = data[mbtcp["num_objects"]["start"]:mbtcp["num_objects"]["end"]]
        print("{} [+] Number of Objects: {}{}{}".format(Fore.BLUE, Fore.YELLOW, dec(num_objects), Fore.RESET))
        print("")
        
        object_start = mbtcp["object_id"]["start"]
        for i in range(dec(num_objects)):
            object              = {}
            end_id              = object_start + mbtcp["object_id"]["length"]
            object["id"]        = data[object_start:end_id]
            end_len             = end_id + mbtcp["objects_len"]["length"]
            object["len"]       = data[end_id:end_len] # len in bytes
            end_str_value       = end_len + (dec(object["len"]) * 2)
            object["str_value"] = data[end_len:end_str_value]

            try:
                object["name"] = object_name[dec(object["id"])]
            except:
                object["name"] = "Name X"

            print("{} [*] {}{}: {}{}{}".format(
                Fore.WHITE,
                Fore.GREEN,
                object["name"],
                Fore.YELLOW,
                binascii.unhexlify(object["str_value"]).decode("utf-8"),
                Fore.RESET
            ))

            object_start = end_str_value
        print("")
    except Exception as e:
        print("{} [!] MODBUS - did not receive data.{}".format(Fore.RED, Fore.RESET))
        print(e)
        
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
client.send(payload.encode())
data = client.recv(bufsize)
client.close()

parse_response(data)