#! /bin/python3

#############################################################################
# script to copy raw MAIR-E instrument data from RAF ground station
# computer to MethaneSAT Google Cloud Platform (GCP) bucket.
# can be run on either RAF station computer.
#############################################################################

import os
import re
import sys
import string
import smtplib
from email.mime.text import MIMEText

# Variable set up
#bucket_url = "gs://msat-prod-methaneair-upload"
bucket_url = "gs://maire_test"
# Function to copy data
def gcpCopy():
    global flight_date
    global copy_process
    flight_date = input('Please enter the flight date in format YYYYMMDD: ')
    drive_name = str(os.listdir('/run/media/ads')[0])
    print('Drive name: ' + drive_name + ' detected.')
    try:
        command = 'time ionice -c 2 -n 7 gsutil -m cp -r '+ '/run/media/ads/' + drive_name + '/' + flight_date + ' ' + bucket_url
        os.system(command)
        copy_process = True
    except Exception as e:
        print(e)
        copy_process = False
    return flight_date, copy_process

def sendMail(flight_date):

    try:
        msg = MIMEText('gsutil cp process for MAIR-E flight date: ' + flight_date + ' complete. \n\nCheck GCP bucket :' + bucket_url + '\n\nPlease feel free to contact Taylor Thomas (NCAR) at taylort@ucar.edu or (720) 680-4395 with questions.')
        msg['Subject'] = flight_date + ' MAIR-E GCP Data Transfer Process'
        msg['From'] = 'ads@groundstation'
        msg['To'] = 'tmelendez@methanesat.org, nlofaso@methanesat.org, jacob.hohl@cfa.harvard.edu, jkostinek@g.harvard.edu, taylort@ucar.edu, mpaxton@ucar.edu, ptsai@ucar.edu, cwolff@ucar.edu'
        s = smtplib.SMTP('localhost')
        s.sendmail('ads@groundstation','taylort@ucar.edu', msg.as_string())
        s.quit()
    except Exception as e:
        print(e)

# Main function
def main():
    gcpCopy()
    if copy_process == True:
        try:
            sendMail(flight_date)
        except Exception as e:
            print(e)
    else:
        print('No email sent.')

if __name__ == "__main__":
    main()
