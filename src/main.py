import socket
import sys
import json

def formatMessage1(record):
    
    
    decoded_record = record.decode("utf-8")
    new_record_list = decoded_record.split("|!|")
    config_file = open("config.json")
    dataConfig = json.load(config_file)

    counter = -1
    print(new_record_list)
    
    # ADD ERROR CHECKING HERE, THIS WHERE YOU MATCH THE CONTENT WITH FORMAT IN CONFIG
    for i in dataConfig["format"]:
        counter = counter + 1
        print(i)
        dataConfig["format"][i] = new_record_list[counter]
        print(counter)

    formatted_message = dataConfig["formatted_message"].format(**dataConfig["format"])
    print(formatted_message)
     
        
        
        
    # how many formats given
    # Can i asscoiate the value for format and then just print?
    # probably
  
    # PUT THE CONTENT IN ORDER OF THE FORMAT 
    
   # level = new_record_list[0]
   # ip = new_record_list[1]
    #date_time = new_record_list[2] 
   # time_zone = new_record_list[3]
   # content = new_record_list[4]
   #
    
   #formatted_message = f"[{level}] {ip} {date_time} {time_zone} - {content}\n"
    
   # formatted_message = f"[{level}] [{ip}] [{date_time} {time_zone}] - {content}\n"
    
   # print(formatted_message)

    return "formatted_message"

    
# Have to use JSON for the information
def formatMessage(record):
    
    
    decoded_record = record.decode("utf-8")
    new_record_list = decoded_record.split("|!|")

    # PUT THE CONTENT IN ORDER OF THE FORMAT 
    
    level = new_record_list[0]
    ip = new_record_list[1]
    date_time = new_record_list[2] 
    time_zone = new_record_list[3]
    content = new_record_list[4]
    
    
   #formatted_message = f"[{level}] {ip} {date_time} {time_zone} - {content}\n"
    
    formatted_message = f"[{level}] [{ip}] [{date_time} {time_zone}] - {content}\n"
    
    print(formatted_message)

    return formatted_message
 
def writeIntoLog(log_path, record):
    
    
    # When logging get instance id and attach that to log file name and then just date
    try:        
        with open(log_path, 'a') as file:
            formatted_message = formatMessage1(record)
            file.write(formatted_message)
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
                  







