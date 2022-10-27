"""
Renita Zaparde 
10/26/2022

This file has been updated to improve error handling and remove extraneous variables! 
README has not yet been updated. 

main function: 
- Sends email alerts for clinicians outside of their designated safety zones

sendEmail function: 
- Sends emails to specified recipient with an inputted message body

"""

import requests
import json
import smtplib, ssl
from shapely.geometry import Point, LineString, Polygon
from datetime import datetime 
import time 

def main(): 
    # Check clinician statuses for all clinician Ids between 1 and 6 (inclusive)
    for clinicianId in range(1,7): 
        # get clinician status by making a request to Clinician Status API 
        url = 'https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus/{}'.format(clinicianId)
        response = requests.get(url,auth=None)

        if response.ok: 
            # Error handling in case of invalid inputs not caught by response.ok 
            try: 
                # variables for clinician's location and flag to track if they are in their safe zone
                location = None
                is_safe_flag = False
                # convert the json string (response.content) into a Python object 
                clinician_data = json.loads(response.content)

                for feat in clinician_data["features"]: 
                    # Store the clinician's current coordinates 
                    if feat["geometry"]["type"]=="Point": 
                        location = Point(feat["geometry"]["coordinates"])
                    # Check if they are in their designated polygon (safety zone) -- See README for technical choices 
                    else: 
                        # used Polygon and LineString from shapely.geometry
                        coordinates = feat["geometry"]["coordinates"][0]
                        polygon = Polygon(coordinates)
                        line = LineString(coordinates) 
                        # location in polygon and distance from line: http://docs.jquerygeo.com/geo/contains.html, https://www.geeksforgeeks.org/python-sympy-polygon-distance-method/
                        if polygon.contains(location) or line.distance(location) < 1e-10: 
                            is_safe_flag = True

                # immediately send alert for missing clinician (no need for cliniciansOutOfRange list)
                if not is_safe_flag: 
                    print("Missing clinician: {}".format(clinicianId))
                    # Get the current time (local timezone) to report when the clinician went missing
                    missing_time = datetime.now().strftime('%I:%M %p')

                    # Send email for the clinician that is missing at this time
                    # NOTE: for efficiency, could send one email with all IDs of missing clinicians!  
                    subject = "Alert - Missing Phlebotomist ID: {}".format(clinicianId)
                    msg = "Hi, \n\nWe have a phlebotomist out of their designated safety zone! Phlebotomist ID: {}.\n\nTime they went missing from their zone: {}\n\nFor debugging/confirmation purposes, I've included the point and polygon coordinates below:\n\n{}".format(clinicianId, missing_time, response.text)
                    sendEmail(subject, msg)

            # handling any invalid input errors (cause KeyError in accessing "features" in clinician_data)
            except Exception as err:
                print(clinicianId)=
                subject = "Invalid Input!"
                msg = "Hi, \n\nWe tried using an invalid input and received the following error: {}.\n\n Try again with correct inputs!".format(response.text)
                sendEmail(subject, msg)

        else: 
            # If endpoint does not return properly, send email with a warning for that input -- see README for details
            subject = "Endpoint Not Returning"
            msg = "Hi, \n\nOur endpoint is not returning for some reason. We received the following error: {}.".format(response.text)
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
        # login to "renita.coding.test@gmail.com" and send the email with message body
        server.login(sender, gmail_app_password)
        server.sendmail(sender, recipient, message)
        print("Email sent.")
        server.quit()
    # handing any errors in case email is not sent 
    except Exception as err:
        print(err)

# Driver code
if __name__=="__main__": 
    # while True: 
    #     main()
    #     time.sleep(45)
    main()
