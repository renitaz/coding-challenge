"""
Renita Zaparde 
10/24/2022

For implementation details of the following functions, see README file.

main function: 
- Sends email alerts for clinicians outside of their designated safety zones

sendEmail function: 
- Sends emails to specified recipient with an inputted message body

"""

import requests
import json
import smtplib, ssl
from shapely.geometry import shape, Point, LineString, MultiLineString
from datetime import datetime 
import time 

def main(): 
    # list to store IDs of clinicians out of their range 
    cliniciansOutOfRange = []
    # dictionary (ID:response.text) used for debugging/confirming results in emails 
    clinicianResponseText = {}

    # Check clinician statuses for all clinician Ids between 1 and 6 (inclusive)
    for clinicianId in range(1,7): 
        # get clinician status by making a request to Clinician Status API 
        url = 'https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus/{}'.format(clinicianId)
        response = requests.get(url,auth=None)

        if response.ok: 
            # convert the json string (response.content) into a Python object 
            clinician_data = json.loads(response.content)
            clinicianResponseText[clinicianId] = response.text

            # Error handling for invalid inputs not caught by response.ok -- see README for details 
            check_input = url[76:]
            if not check_input.isnumeric() or int(check_input) not in range(1,8):
                subject = "Invalid Input!"
                msg = "Hi, \n\nWe tried using an invalid input and received the following error: {}.\n\n Try again with correct inputs!".format(response.text)
                sendEmail(subject, msg)
                continue

            # variables for clinician's location and flag to track if they are in their safe zone
            location = None
            is_safe_flag = False

            for feat in clinician_data["features"]: 
                # Store the clinician's current coordinates 
                if feat["geometry"]["type"]=="Point": 
                    location = Point(feat["geometry"]["coordinates"])
                # Check if they are in their designated polygon (safety zone)
                # See README for technical choices 
                else: 
                    # used shape and LineString from shapely.geometry
                    polygon = shape(feat["geometry"])
                    line = LineString(feat["geometry"]["coordinates"][0])
                    dist = line.distance(location)
                    # location in polygon and distance from line 
                    if polygon.contains(location) or dist < 1e-10: 
                        is_safe_flag = True

            if not is_safe_flag: 
                cliniciansOutOfRange.append(clinicianId)
            # print("Clinician {} is in safe zone: ".format(clinicianId) + str(is_safe_flag))

        else: 
            # If endpoint does not return properly, send email with a warning for that input -- see README for details
            subject = "Endpoint Not Returning"
            msg = "Hi, \n\nOur endpoint is not returning for some reason. We received the following error: {}.".format(response.text)
            sendEmail(subject, msg)
            # prints the HTTP error code description 
            # response.raise_for_status() 

    # For debugging: 
    print(cliniciansOutOfRange)
    for i in cliniciansOutOfRange: 
        print(clinicianResponseText[i])
    print()

    # Get the current time (local timezone) to report when the clinician went missing
    missing_time = datetime.now().strftime('%I:%M %p')

    # Send email for every clinician that is missing at this time
    # NOTE: for efficiency, could send one email with all IDs of missing clinicians!  
    for clinicianId in cliniciansOutOfRange:
        subject = "Alert - Missing Phlebotomist ID: {}".format(clinicianId)
        msg = "Hi, \n\nWe have a phlebotomist out of their designated safety zone! Phlebotomist ID: {}.\n\nTime they went missing from their zone: {}\n\nFor debugging--point and polygon coordinates:\n\n{}".format(clinicianId, missing_time, clinicianResponseText[clinicianId])
        sendEmail(subject, msg)


# Function to send plain text emails over unsecured SMTP connection (encrypted with .starttls())
def sendEmail(subject, msg):
    context = ssl.create_default_context()
    sender = "renita.coding.test@gmail.com"
    recipient = "renita.coding.test@gmail.com"
    gmail_app_password = "rlvcobgrvezsjnoj"
    # formatted message this way to update Subject line in gmail 
    message = 'Subject: {}\n\n{}'.format(subject, msg)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587) # vs port 465 for SSL 
        server.ehlo() 
        # encrypt the connection
        server.starttls(context=context) 
        server.ehlo() 
        # login to "renita.coding.test@gmail.com" and send the email 
        server.login(sender, gmail_app_password)
        server.sendmail(sender, recipient, message)
        print("Email sent.")
        server.quit()
    # handing any errors in case email is not sent 
    except Exception as err:
        print(err)

# Driver code
if __name__=="__main__": 
    # for i in range(60): 
    #     main()
    main()
