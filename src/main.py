import socket
import sys
import json


# Open JSON

# Read, IP, PORT, and File Location
# Store in variables


config_file = open("config.json")

dataConfig = json.load(config_file)

service_ip = dataConfig["log_service_config"]["ip"]

service_port = dataConfig["log_service_config"]["port"]

log_location = dataConfig["log_service_config"]["log_location"]

print(service_ip, service_port, log_location)
