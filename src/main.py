import socket
import sys
import json

import threading
INVALID_LOG_NOT_WRITTEN_MESSAGE = "Invalid Log Record Given, Not Written"
def formatMessage(record, format_config):
    
    decoded_record = record.decode("unicode_escape")
    record_in_json = json.loads(decoded_record)
    
    print(record_in_json)
    
    if(format_config["format_1"].keys() == record_in_json.keys()):
        print("same")
        formatted_message = format_config["formatted_message_1"].format(**record_in_json)
        formatted_message += "\n"   
    elif format_config["format_2"].keys() == record_in_json.keys():
        print("Test")
        formatted_message = json.dumps(record_in_json, indent=4)
        formatted_message += "\n"   
    else:
        print("not same")
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
        
                  