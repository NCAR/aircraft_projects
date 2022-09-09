#!/usr/bin/env python3

#############################################################################
# script to copy raw MAIR-E instrument data from RAF ground station
# computer to MethaneSAT Google Cloud Platform (GCP) bucket.
# can be run on either RAF station computer.
#############################################################################
import os
import smtplib
from email.mime.text import MIMEText

# Variable set up
#drive_name = "Drive2"
#flight_date = "YYYYMMDD"
bucket_url = "gs://maire_test"

# Function to copy data
def gcpCopy():

        try:
            os('time ionice -c 2 -n 7 gsutil -m cp -r  /home/data/MAIRE/' + bucket_url)
            #os('time ionice -c 2 -n 7 gsutil -m cp -r /run/media/ads/' + drive_name + '/' + flight_date + ' ' + bucket_url)
            msg = MIMEText('Data available at: ' + bucket_url )
            msg['Subject'] = 'MAIR-E GCP Raw Instrument Data Transfer Complete'
            msg['From'] = 'ads@groundstation'
            msg['To'] = 'taylort@ucar.edu'
            s = smtplib.SMTP('localhost')
            s.sendmail('ads@groundstation','taylort@ucar.edu', msg.as_string())
            s.quit()
        except Exception as e:
            print(e)

# Main function
def main():
    gcpCopy()

if __name__ == "__main__":
    main()
