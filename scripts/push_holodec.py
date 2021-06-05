#!/usr/bin/python
#
# Script written for SPICULE to move HOLODEC files from the ground station to 
# the project FTP area.
#
###############################################################################
import os
import sys
import ftplib
import smtplib
from email.mime.text import MIMEText


# If you print an error message to the screen, also print it to the email.
def print_message(message):
    global final_message
    try:
        final_message
    except NameError:
        final_message = ''
    print message
    final_message = final_message + message + "\n"

def read_env(env_var):
  try:
    var =       os.environ[env_var]
    return(var)
  except KeyError:
    print "Please set the environment variable "+env_var
    sys.exit(1)

def main():

    # Read in some env vars
    project = read_env("PROJECT")
    print "project = " + project

    # Get disk name (e.g. HOLO-02). Don't need entire path. Get email.
    disk = raw_input('Input disk name (e.g. HOLO-02):')
    print_message("Reading disk " + disk)
    email = raw_input('Input email address to send results:')

    # Hardcode path and ftp site
    disk_data_dir =  '/run/media/ads/' + disk + '/holodec' + '/Camera 1/'
    ftp_site = 'ftp.eol.ucar.edu'
    ftp_data_dir = 'pub/data/incoming/spicule/EOL_data/holodec'

    # ftp files from disk_data_dir to ftp_site:ftp_data_dir
    # will end out in /net/ftp/<ftp_data_dir>
    try:
        print_message('Opening connection to ftp.eol.ucar.edu')
        ftp = ftplib.FTP(ftp_site)
        ftp.login("anonymous", email)
        ftp.cwd(ftp_data_dir)
    except ftplib.all_errors as e:
        print_message('Error connecting to FTP site: ' + e)
        ftp.quit()

    print_message("Putting files: ")
    for file_name in os.listdir(disk_data_dir):
        print_message(disk_data_dir + '/' + file_name)
        try:
            file = open(disk_data_dir + '/' + file_name, 'r')
            ftp.storbinary('STOR ' + file_name, file)
            file.close()
        except ftplib.all_errors as e:
            print_message('Error writing ' + file_name + ' to '+ ftp_site + \
                          ':/' + ftp_data_dir)
            print e
        

    ftp.quit()

    # send email that script has completed
    print_message('Successful completion of push_holodec script')
    msg = MIMEText(final_message)
    msg['Subject'] = 'push_holodec message for ' + project + ' disk ' + disk
    msg['From'] = 'ads@groundstation'
    msg['To'] = email

    s = smtplib.SMTP('localhost')
    s.sendmail('ads@groundstation',email, msg.as_string())
    s.quit()

    print "\r\nClose window to exit."
    sys.exit(1)


if __name__ == "__main__":
    main()
