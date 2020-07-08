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
try:
    port = int(sys.argv[2])
except:
    port = 502


bufsize = 2048
unit_id = "\x00"
payload = (
    "\x44\x62" # Transaction Identifier
    "\x00\x00" # Protocol Identifier
    "\x00\x05" # Length
    "{}"       # Unit Identifier
    "\x2b"     # .010 1011 = Function Code: Encapsulated Interface Transport (43)
    "\x0e"     # MEI type: Read Device Identification (14)
    "\x03"     # Read Device ID: Extended Device Identification (3)
    "\x00"     # Object ID: VendorName (0)
).format(unit_id)

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

# Main Modbus exception codes
def handle_exception_codes(code):
    if code == b'ab01':
        print("{} [!] Illegal Function: Function code received in the query is not recognized or allowed by slave.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab02':
        print("{} [!] Illegal Data Address: Data address of some or all the required entities are not allowed or do not exist in slave.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab03':
        print("{} [!] Illegal Data Value: Value is not accepted by slave.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab04':
        print("{} [!] Slave Device Failure: Unrecoverable error occurred while slave was attempting to perform requested action.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab05':
        print("{} [!] Acknowledge: Slave has accepted request and is processing it, but a long duration of time is required.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab06':
        print("{} [!] Slave Device Busy: Slave is engaged in processing a long-duration command.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab07':
        print("{} [!] Negative Acknowledge: Slave cannot perform the programming functions.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab08':
        print("{} [!] Memory Parity Error: Slave detected a parity error in memory.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab0a':
        print("{} [!]  Gateway Path Unavailable: Specialized for Modbus gateways. Indicates a misconfigured gateway.{}".format(Fore.RED, Fore.RESET))
    elif code == b'ab0b':
        print("{} [!] Gateway Target Device Failed to Respond: Specialized for Modbus gateways.{}".format(Fore.RED, Fore.RESET))
    else:
        print("{} [!] MODBUS - received incorrect data {}{}".format(Fore.RED, code, Fore.RESET))

def parse_response(data):
    data = binascii.hexlify(data)
    unit_id = data[mbtcp["unit_id"]["start"]:mbtcp["unit_id"]["end"]]
    
    print("")
    print("{} [+] Host:\t\t{}{}{}".format(Fore.BLUE, Fore.RED, host, Fore.RESET))
    print("{} [+] Port:\t\t{}{}{}".format(Fore.BLUE, Fore.RED, str(port), Fore.RESET))
    print("{} [+] Unit Identifier:\t{}{}{}".format(Fore.BLUE, Fore.YELLOW, unit_id.decode("utf-8"), Fore.RESET))

    if data[mbtcp["func_code"]["start"]:mbtcp["mei"]["end"]] == b'2b0e':
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

    else:
        print("")
        handle_exception_codes(data[mbtcp["func_code"]["start"]:mbtcp["mei"]["end"]])
        print("")

        
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((host, port))
    client.send(payload.encode())
    data = client.recv(bufsize)
    client.close()
    parse_response(data)
except Exception as e:
    print("\n{} [!] MODBUS - did not receive data.{}\n".format(Fore.RED, Fore.RESET))
    print(e)

