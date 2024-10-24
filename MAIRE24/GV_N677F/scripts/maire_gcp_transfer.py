#! /bin/python3

#############################################################################
# script to copy raw MAIR-E instrument data from the eol-airplane Windows
# laptop computer to MethaneSAT Google Cloud Platform (GCP) bucket.
#
# NOTE: This script was used for MAIRE (2022) and has not been tested for
# MAIRE2024. It is just copied here in prep for using it for this project.
#############################################################################

import os
import re
import sys
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Variable set up
bucket_url = "gs://msat-prod-data-methaneair-upload"
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
        msg = MIMEMultipart()
        msg["Subject"] = flight_date + ' MAIR-E GCP Data Transfer Process'
        msg["From"] = 'maire@eol-airplane'
        msg["To"] = "janine@ucar.edu,tmelendez@methanesat.org,jfranklin@g.harvard.edu,bkluo@cfa.harvard.edu,cdewerd@ucar.edu,nlofaso@methanesat.org,jacob.hohl@cfa.harvard.edu,jkostinek@g.harvard.edu,mpaxton@ucar.edu,ptsai@ucar.edu,cwolff@ucar.edu"
        body = MIMEText('gsutil cp process for MAIR-E flight date: ' + flight_date + ' complete. \n\nCheck GCP bucket :' + bucket_url)
        msg.attach(body)
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
        smtp.quit()
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
