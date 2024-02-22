import socket
import sys
import json



def formatMessage(record):
    
    decoded_record = record.decode("unicode_escape")
    config_file = open("config.json")
    data_config = json.load(config_file)
    record_in_json = json.loads(decoded_record)

    
    if(data_config["format"].keys() == record_in_json.keys()):
        print("same")
        formatted_message = dataConfig["formatted_message"].format(**record_in_json)

        formatted_message += "\n"   
    else:
        print("not same")
        # DO I Send back message?
        formatted_message = "Invalid Log Record Given\n"
 

    return formatted_message
 #https://pypi.org/project/pyrate-limiter/
def writeIntoLog(log_path, record):
    
    # When logging get instance id and attach that to log file name and then just date
    try:        
        with open(log_path, 'a') as file:
            formatted_message = formatMessage(record)
            file.write(formatted_message)
    except IOError:
        print("ERROR: record could not be written to file")
        # Send a message back that something went wrong 
            


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
        
        data = conn.recv(2054)
        if data:
            writeIntoLog(log_location, data)
                  







