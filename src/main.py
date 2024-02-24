import socket
import sys
import json

import threading

# Create function to validate confign not messed up and thus prevents misconfiguration

def checkIfSeverityGivenCorrect(record_in_json, required_severity):
    
    severity_found = False
   
    for severity in required_severity:
        # DO TRY EXCEPT HERE SO THAT IF USER FIDDLES WITH ANYTHING IT WILL SNED INVALID
         if severity == record_in_json.get("severity"):
            severity_found = True
    
    return severity_found


def checkIfLevelGivenCorrect(record_in_json, required_levels):
    
    level_found = False
    for level in required_levels:
        # DO TRY EXCEPT HERE SO THAT IF USER FIDDLES WITH ANYTHING IT WILL SNED INVALID
        if (level == record_in_json.get("level")):
            level_found = True
    
    return level_found                                            
                           
INVALID_LOG_NOT_WRITTEN_MESSAGE = "Invalid Log Record Given, Not Written"

def formatMessage(record, format_config):
    
    decoded_record = record.decode("unicode_escape")
    record_in_json = json.loads(decoded_record)
    
    print(record_in_json)
    # Check if format 1 matches record, check if format 2 matches record else invalid format
    if(format_config["format_1"]["structure"].keys() == record_in_json.keys()):
        # Check if level found in record matches required
        found_level = checkIfLevelGivenCorrect(record_in_json, format_config["format_1"]["required_levels"])
        print(found_level)
        if(found_level == False):
            formatted_message = INVALID_LOG_NOT_WRITTEN_MESSAGE
        else:
            formatted_message = json.dumps(record_in_json, indent=4)
            formatted_message += "\n"   
    elif format_config["format_2"]["structure"].keys() == record_in_json.keys():
         # Check if severity found in record matches required
        found_severity= checkIfSeverityGivenCorrect(record_in_json, format_config["format_2"]["required_severity"])
        if(found_severity == False):
            formatted_message = INVALID_LOG_NOT_WRITTEN_MESSAGE
        else:
            formatted_message = json.dumps(record_in_json, indent=4)
            formatted_message += "\n"   
    else:
        # DO I Send back message?
        formatted_message = INVALID_LOG_NOT_WRITTEN_MESSAGE
 
    
    return formatted_message
 #https://pypi.org/project/pyrate-limiter/

lock = threading.Lock()
            
def writeIntoLogWorker(record, format_config, conn):
   
    log_location = format_config["log_service_config"]["log_location"]
    if record:
        lock.acquire()
        try:        
            with open(log_location, 'a') as file:
                formatted_message = formatMessage(record, format_config)
                if formatted_message == INVALID_LOG_NOT_WRITTEN_MESSAGE:
                    conn.sendall(bytes(formatted_message, 'utf-8'))
                    print("test555")
                # Should add a timeout in case wait takes too long then skip to stop hanging of service
                else:
                    file.write(formatted_message)
                    conn.sendall(bytes("0", 'utf-8'))
                lock.release()
        except Exception as e:
            print(e)
            
 #except IOError:
          #  print("ERROR: record could not be written to file")

config_file = open("config.json")

dataConfig = json.load(config_file)

service_ip = dataConfig["log_service_config"]["ip"]

service_port = dataConfig["log_service_config"]["port"]

log_location = dataConfig["log_service_config"]["log_location"]


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = (service_ip, int(service_port))

sock.bind(address)

sock.listen()

while (True):
    
    print("waiting for connection")
    conn, addr = sock.accept()
    print("Connected")
    try:
        record = conn.recv(2054)
        writeIntoLogWorker(record, dataConfig, conn)
    except Exception as e:
        print(f"Error with connection :{e}")
    finally:
        conn.close()

        
        
# Could have it so that each time a writer is going and it's done it will decrement and incr 
        
                  