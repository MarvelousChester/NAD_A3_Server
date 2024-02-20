import socket
import sys
import json

def writeIntoLog(log_path, record):
    
    
    # When logging get instance id and attach that to log file name and then just date
    try:        
        with open(log_path, 'ab') as file:
            content = file.write(record)
    except IOError:
        print("ERROR: record could not be written to file")
        # Send a message back that something went wrong 
            


# Open JSON

# Read, IP, PORT, and File Location
# Store in variables


config_file = open("config.json")

dataConfig = json.load(config_file)

service_ip = dataConfig["log_service_config"]["ip"]

service_port = dataConfig["log_service_config"]["port"]

log_location = dataConfig["log_service_config"]["log_location"]


# setting up listener

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = (service_ip, int(service_port))

sock.bind(address)

sock.listen()
while True:
        print("waiting for connection")
        conn, addr = sock.accept()
        print("Connected")
        
        data = conn.recv(1024)
        if data:
            writeIntoLog(log_location, data)
                  
       




