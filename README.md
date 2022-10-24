Renita Zaparde | Take Home Assignment | 10/24/2022


**Usage:** python main.py 

This program checks the clinician statuses every minute and sends an email alert to the specified address if any clinician is outside of their designated safety zone. 

**Files in this project:**
- main.py 
- README.md 


**------- IMPLEMENTATION -------**

**---- main function ----**

This function uses ```sendEmail()``` to send alerts about clinicians outside of their designated safety zones, reporting their clinicianId and the time they went missing (local timezone). 

_For each clinician we do the following:_
- First, the function gets the clinician statuses for all valid IDs [1, 6] by calling the Clinician Status API. If the request is valid (see error handling below), we convert the response content (via ```json.loads()```) into a Python object: ```clinician_data```. 

- Now, we check that the clinician is in the safety zone. From ```clinician_data```, we extract the clinician's ```location``` and initially set the ```is_safe_flag``` to False. 

- For each feature in ```clinician_data``` we do the following: 
    - If the feature's geometry type is ```"Point"```, we store these coordinates in ```location```. 
    - Else (if the feature's geometry type is ```"Polygon"```), we initialize a ```shape``` (polygon) using this feature's geometry information. We also initialize a ```LineString``` object using the feature's geometry coordinates array, and calculate the distance between the location and the line.
    - Then, if the location is in the polygon or if the distance is less than 1x10^-10 (essentially checking if the distance is zero), then we set ```is_safe_flag``` to True.
> NOTE: Using ```"line.within(location)"``` incorrectly returned False, so I chose to calculate and check the distance instead. 

- If ```is_safe_flag``` is False, we append the ```clinicianId``` to our array ```cliniciansOutOfRange```, which tracks missing clinicians. 

- Now, we want to send an email alert to the recipient address with the information for each clinician that is missing. So, we iterate through ```cliniciansOutOfRange```, update the message body with the relevant ```clinicianId``` and the current time (AM/PM format, local timezone), and send the email alert. 


_Error Handling:_

1. The endpoint does not return properly:
- This error usually occurs when there is no input given for the ```clinicianId```. 
    - Example: if we input an empty string, i.e. we try to call the API using ```".../clinicianstatus/"```, we get the response: ```"{"message":"Missing Authentication Token"}"```. 
    - We send an email with the subject, "Endpoint Not Returning", and the response text. 

2. We call the API with an invalid input: 
- This error is not caught by ```response.ok``` since the response still outputs status 200. However, once we attempt to extract information from ```clinician_data```, there is a ```KeyError``` because the input is incorrect. To avoid this, once inside the if-clause with the ```response.ok``` condition, we check two conditions based on the string ```url[76:]```, which is after ```.../clinicianstatus/____```:
    - I. If the string is not numeric, it cannot be a valid clinicianId. 
        - Example #1: if we input an invalid string such as ```"asdf"```, i.e. we try to call the API using ```".../clinicianstatus/asdf"```, we get the response: ```{"error":"Invalid clinicianID","clinicianID":"asdf"}```
    
    - II. If the string is not in the range [1,7] inclusive, it is be a valid clinicianId. Note: I included 7 here because it is technically valid. 
        - Example #2: if we input an invalid clinicianId such as ```"9"```, i.e. we try to call the API using ```".../clinicianstatus/9"```, we get the response: ```{"error":"Invalid clinicianID","clinicianID":"9"}```
    
    - In either of these cases, we send an email with the subject, "Invalid Input!", and the response text. 



**---- sendEmail function ----**

This function uses Python's built-in ```smtplib``` module to send emails from the sender address to the specified recipient, using the parameter strings (```subject``` and ```msg```) in the message body of the email. 

> Note: I chose to use the TLS protocol because I'm more familiar with it! I also created my own gmail account, ```"renita.coding.test@gmail.com"```, for this assignment. If you'd like access to it, let me know and I can send you the password! 

Here, we try to create an unsecured SMTP connection, and encrypt the connection with ```.starttls()```. If this is successful, we then log into the testing email (using the generated gmail app password) and send the email to the specifiend recipient. We then quit the server. 

The exception case handles any possible errors thrown while attempting to send an email. 



**---- Driver Code ----**

Finally, the driver code implements the ```main()```. I've set it up to check the clinician statuses every minute for a total duration of one hour. 
- I chose to poll the API every minute because it was more practical than checking every 10 seconds vs. every 5 minutes. 
    - If we checked every 10 seconds, we could overload the server :( 
    - If we checked very 5 minutes, we may miss sending a necessary alert email within the required timeframe! 

> Note: If the for loop is replaced with ```while True:```, the program will run indefinitely. I chose to keep the for loop and cap the program at one check/min (for roughly one hour total). 

