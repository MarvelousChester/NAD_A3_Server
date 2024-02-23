import socket
import sys
import json

from pyrate_limiter import Duration, Rate, Limiter, BucketFullException

rate = Rate(10, Duration.SECOND * 1)
limiter = Limiter(rate)




import threading


def formatMessage(record, format_config):
    
    decoded_record = record.decode("unicode_escape")
    record_in_json = json.loads(decoded_record)

    
    if(format_config["format"].keys() == record_in_json.keys()):
        print("same")
        formatted_message = format_config["formatted_message"].format(**record_in_json)
        formatted_message += "\n"   
    else:
        print("not same")
        # DO I Send back message?
        formatted_message = "Invalid Log Record Given\n"
        formatted_message += "\n"   
 
    return formatted_message
 #https://pypi.org/project/pyrate-limiter/

lock = threading.Lock()

MAX_LOG_CALLS_PER_MINUTE = 60
ONE_MINUTE = 60

@RateLimiter(max_calls=10, period=1)     
def writeIntoLogWorker(record, format_config):
   
    log_location = format_config["log_service_config"]["log_location"]
    if record:
        lock.acquire()
        try:        
            with open(log_location, 'a') as file:
                formatted_message = formatMessage(record, format_config)
                file.write(formatted_message)
                # Should add a timeout in case wait takes too long then skip to stop hanging of service
                lock.release()
        except IOError:
            print("ERROR: record could not be written to file")


config_file = open("config.json")

dataConfig = json.load(config_file)

service_ip = dataConfig["log_service_config"]["ip"]

service_port = dataConfig["log_service_config"]["port"]

log_location = dataConfig["log_service_config"]["log_location"]


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

address = (service_ip, int(service_port))

sock.bind(address)

sock.listen()


# count number of requests sent from client

# IF number of request within specific time reached
    # Send message that 15 second timeout

# Continue

while (True):
    
    print("waiting for connection")
    conn, addr = sock.accept()
    print("Connected")
    try:
       
        record = conn.recv(2054)
        x = threading.Thread(target=writeIntoLogWorker, args=(record, dataConfig,))
        x.start()
    except Exception as e:
        print(f"Error with connection :{e}")
    finally:
        conn.close()

        
        
# Could have it so that each time a writer is going and it's done it will decrement and incr 
        
                  