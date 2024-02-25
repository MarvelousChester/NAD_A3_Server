# Required Format

IF using format 1: you must use Level,Unique Identifier and have content
IF using format 2: you must use Severity, Unique Identifier and have content

other wise you can customize, add things as long as the client you are sending from does it properly so using objects

# How to Customize

- Don't touch required_levels or severity
- Can move the structure according to how json object is passed

# Messages Communication

Will send back "Invalid Log Record Given, Not Written" if invalid format given
Will send back "(-2)~" prepended to a message to indicate you have exceeded request per minute
