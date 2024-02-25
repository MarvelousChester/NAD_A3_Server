import socket
import sys
import json
import threading
from tendo import singleton
import time

MAX_REQUESTS_PER_MINUTE = 1000
MINUTE = 60
ADD_TO_KEEP_TRACK  = 2



class RateLimiter:
    
    def __init__(self):
        # Connection must be something else, must be None I believe
        self.tracker = { "connection": {"requests_counted_per_minute" : None, "time_stamp" : None}}
       

    # Name: can_make_requests
    # Purpose: Checks if the connection ip can make a request and if not it return a bool to indicate to read the response or not
    # Parameters: client_indetifier: the public facing ip to identify where coming from 
    # Returns:
    #   True if client can make a logging request        
    #   False if client cannot make a request and must wait
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
            new_client = {client_identifier : { "requests_counted_per_minute" : 1, "time_stamp" : current_time_stamp}}
            self.tracker.update(new_client)
            return True
    # Name: add_to_tracker
    # Purpose: Add ip to tracker so it can track when last connection time stamp
    # Parameters: client_indetifier: the public facing ip to identify where coming from 
    # Returns: NONE
    def add_to_tracker(self, client_identifier):
        current_time_stamp = time.time()
        new_client = {client_identifier : { "requests_counted_per_minute" : 1, "time_stamp" : current_time_stamp}}
        self.tracker.update(new_client)
    

# Name: checkIfSeverityGivenCorrect
# Purpose: Checks if the log record has given the proper severities for format
# Parameters: 
#           record_in_json: the record that was passed for logging in json format to check the severities 
#           required_severity: json record of the severities that to check against
# Returns: 
#      True: IF found
#      False: Not matching 
def checkIfSeverityGivenCorrect(record_in_json, required_severity):
    
    severity_found = False
   
    for severity in required_severity:
        # DO TRY EXCEPT HERE SO THAT IF USER FIDDLES WITH ANYTHING IT WILL SNED INVALID
         if severity == record_in_json.get("severity"):
            severity_found = True
    
    return severity_found


# Name: checkIfLevelGivenCorrect
# Purpose: Checks if the log record has given the proper levels for format
# Parameters: 
#           record_in_json: the record that was passed for logging in json format to check the levels 
#           required_severity: json record of the levels that to check against
# Returns: 
#      True: IF found
#      False: Not matching
def checkIfLevelGivenCorrect(record_in_json, required_levels):
    
    level_found = False
    for level in required_levels:
        # DO TRY EXCEPT HERE SO THAT IF USER FIDDLES WITH ANYTHING IT WILL SNED INVALID
        if (level == record_in_json.get("level")):
            level_found = True
    
    return level_found                                            
                           
INVALID_LOG_NOT_WRITTEN_MESSAGE = "Invalid Log Record Given, Not Written"




def requiredKeysFoundInFormat1(format_config, record):
   decoded_record = record.decode("unicode_escape")
   record_in_json = json.loads(decoded_record)
   
   LEVEL = "level"
   ID = "instance_id"
   content = "content"
   
   required_formatting = {"level", "instance_id", "content"}
   
   required_keys_found = True
   for key in required_formatting:
        if key not in record_in_json:
            required_keys_found = False  # Key missing, set to False and exit loop
        
   return required_keys_found

        
def requiredKeysFoundInFormat2(format_config, record):
   decoded_record = record.decode("unicode_escape")
   record_in_json = json.loads(decoded_record)
   
   required_formatting = {"severity", "instance_id", "message"}
   
   required_keys_found = True
   for key in required_formatting:
        if key not in record_in_json:
            required_keys_found = False
   return required_keys_found

# Name: formatMessage
# Purpose: Given the record it will format it for logging purposes. If the logging format given is matching 1st format it will use the 
#          format message in json to print into log
# Parameters: 
#           record: the record that was passed for logging in bytes to check the levels 
#           format_config: Config to base the format upon
# Returns: Formatted message for writing into file
def formatMessage(record, format_config):
    

    
    # Check if Required Keys Found
    # MOve this into a seperate function
    # 
    #
    #required_keys_found = requiredKeysFoundInFormat1(format_config,record)
    # Merge Required and additional -> Do Comparision if matches record in config
    decoded_record = record.decode("unicode_escape")
    record_in_json = json.loads(decoded_record)
    
    required_keys_found_format1 = requiredKeysFoundInFormat1(format_config, record)
    required_keys_found_format2 = requiredKeysFoundInFormat2(format_config, record)
    if(required_keys_found_format1 == False and required_keys_found_format2 == False):
        return INVALID_LOG_NOT_WRITTEN_MESSAGE
    
   
    
    required_log_format1 = format_config["format_1"]["structure"]["required"]
    additional_log_format1 =  format_config["format_1"]["structure"]["additional"]
    merged_format1 = {**required_log_format1, **additional_log_format1}
    
    
    required_log_format2 = format_config["format_2"]["structure"]["required"]
    additional_log_format2 =  format_config["format_2"]["structure"]["additional"]
    merged_format2 =  {**required_log_format2, **additional_log_format2}
    
   
    # Check if format 1 matches record, check if format 2 matches record else invalid format
    if(merged_format1.keys() == record_in_json.keys()):
        # Check if level found in record matches required
        found_level = checkIfLevelGivenCorrect(record_in_json, format_config["format_1"]["required_levels"])
        if(found_level == False):
            formatted_message = INVALID_LOG_NOT_WRITTEN_MESSAGE
        else:
            formatted_message = format_config["formatted_message_1"].format(**record_in_json)
            formatted_message += "\n"   
    elif merged_format2.keys() == record_in_json.keys():
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

lock = threading.Lock()

# Name: writeIntoLogWorker
# Purpose: Thread function that is used for client to write the log into in the format given by formatMessage function
# Parameters: 
#           format_config: Config to base the format upon
#           conn: connection of the logging client 
#           connection_id: public facing ip of the client
#           rate_limiter: object of rate_limiter used to if to reading data and quit
# Returns: NONE   
def writeIntoLogWorker(format_config, conn, connection_id, rate_limiter):

    can_write = rate_limiter.can_make_requests(connection_id)
    log_location = format_config["log_service_config"]["log_location"]
    try:
        if(can_write == True):
            record = conn.recv(2054)
            with lock:
                if record:
                    try:        
                        with open(log_location, 'a') as file:
                            formatted_message = formatMessage(record, format_config)
                            if formatted_message == INVALID_LOG_NOT_WRITTEN_MESSAGE:
                                conn.sendall(bytes(formatted_message, 'utf-8'))
                            # Should add a timeout in case wait takes too long then skip to stop hanging of service
                            else:
                                file.write(formatted_message)
                                conn.sendall(bytes("0", 'utf-8'))
                    except Exception as e:
                        print(e) 
        else:
            conn.sendall(bytes(f"(-2)~Rate Limited, exceeded max requests per minute:{MAX_REQUESTS_PER_MINUTE}", 'utf-8'))
    except Exception as e:
        print(e)


try:
    me = singleton.SingleInstance()
except singleton.SingleInstanceException as e:
    exit()   
    
def Main():
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

    # Issue might be when the client connects the connection gets overwritten and it doesn't get closed

    while (True):
        # ERORR HAPPENING WITH TRY BLOCk
        conn, addr = sock.accept()
        connection_id = socket.gethostbyname(socket.gethostname())
        try:
            x = threading.Thread(target=writeIntoLogWorker, args=(dataConfig, conn, connection_id, rate_limiter))
            x.start()
        except Exception as e:
            print(f"Error with connection :{e}")

               
        
Main()       
        


# Could have it so that each time a writer is going and it's done it will decrement and incr 
        


# Check if GUID in the tracker


# IF can Write requires add to function
# get the GUID, Place into client identifier
# How to Get GUID?
    # VALIDATE IF KEY MATCHES FORMAT 1 
        # json[][] pass the GUID into ADD tracker
    # Validate if KEY MATCHES FORMAT 2
        # json[][] pass the GUID into ADD tracker
    # Continue normal