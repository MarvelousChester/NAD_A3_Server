import socket
import sys
import json
from ratelimit import limits, sleep_and_retry
import threading

import time

MAX_REQUESTS_PER_MINUTE = 1000
MINUTE = 60

# Create function to validate confign not messed up and thus prevents misconfiguration
class RateLimiter:
    
    def __init__(self):
        # Connection must be something else, must be None I believe
        self.tracker = { "connection": {"requests_counted_per_minute" : None, "time_stamp" : None}}
       

    # returns True if client can make a logging request        
    # Returns False if client cannot make a request and must wait
    def can_make_requests(self, client_identifier):
        # Check if client within tracker
        current_time_stamp = time.time()
        if client_identifier in self.tracker:
            # Get the dictionary with values
            
            connection_request_tracker = self.tracker.get(client_identifier)
            
            counter = connection_request_tracker.get("requests_counted_per_minute")
            time_stamp = connection_request_tracker.get("time_stamp")
            # check if counter has reached max per minute 
            if (current_time_stamp - time_stamp) < MINUTE:
                # Check if within time
                if(counter < MAX_REQUESTS_PER_MINUTE) :
                    self.tracker[client_identifier]["requests_counted_per_minute"] += 1
                    return True
                else:
                    return False
            else: # Reset Connection Request
                print("NOTET$ESTSDTAGAGAF")
                self.tracker[client_identifier]["requests_counted_per_minute"] = 1
                self.tracker[client_identifier]["time_stamp"] = current_time_stamp
                return True
        else:
            # ADD TO DICTIONARY, NEW CLIENT
            new_client = {client_identifier : { "requests_counted_per_minute" : 1, "time_stamp" : current_time_stamp}}
            self.tracker.update(new_client)
            return True
    
    
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


def requiredKeysFoundInFormat1(format_config ,record_to_search):
     for key in format_config["format_1"]["structure"]["required"].keys():
        if(key in record_to_search.keys()):
            required_keys_found = True
        else:
            required_keys_found = False
            break

def formatMessage(record, format_config):
    
    decoded_record = record.decode("unicode_escape")
    record_in_json = json.loads(decoded_record)
    
    required_keys_found = False
    
    # Check if Required Keys Found
    # MOve this into a seperate function
    # 
    #
    required_keys_found = requiredKeysFoundInFormat1(format_config,record_in_json)
    # Merge Required and additional -> Do Comparision if matches record in config
    required_log_format = format_config["format_1"]["structure"]["required"]
    additional_log_format =  format_config["format_1"]["structure"]["additional"]
    merged_format = {**required_log_format, **additional_log_format}
    
   
    # Check if format 1 matches record, check if format 2 matches record else invalid format
    if(merged_format.keys() == record_in_json.keys()):
        # Check if level found in record matches required
        found_level = checkIfLevelGivenCorrect(record_in_json, format_config["format_1"]["required_levels"])
        if(found_level == False):
            formatted_message = INVALID_LOG_NOT_WRITTEN_MESSAGE
        else:
            formatted_message = format_config["formatted_message_1"].format(**record_in_json)
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
        saved_connection = conn
        lock.acquire()
        try:        
            with open(log_location, 'a') as file:
                formatted_message = formatMessage(record, format_config)
                if formatted_message == INVALID_LOG_NOT_WRITTEN_MESSAGE:
                    saved_connection.sendall(bytes(formatted_message, 'utf-8'))
                # Should add a timeout in case wait takes too long then skip to stop hanging of service
                else:
                    file.write(formatted_message)
                    saved_connection.sendall(bytes("0", 'utf-8'))
                conn.close()
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

counter = 0
rate_limiter = RateLimiter()

while (True):
    # ERORR HAPPENING WITH TRY BLOCk
    print("waiting for connection")
    conn, addr = sock.accept()
    print("Connected")
    connection_id = socket.gethostbyname(socket.gethostname())
    try:
        if(rate_limiter.can_make_requests(connection_id) == True):
            record = conn.recv(2054)
            x = threading.Thread(target=writeIntoLogWorker, args=(record, dataConfig, conn))
            x.start()
        else:
            # Send message that they exceeded
            print("TESTING")
            conn.sendall(bytes(f"(-2)~Rate Limited, exceeded max requests per minute:{MAX_REQUESTS_PER_MINUTE}", 'utf-8'))
    except Exception as e:
        print(f"Error with connection :{e}")
        
        
        


# Could have it so that each time a writer is going and it's done it will decrement and incr 
        

