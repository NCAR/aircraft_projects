#!/usr/bin/python
#
# Script written for SPICULE to move HOLODEC files from the ground station to 
# the project FTP area.
#
###############################################################################
import os
import ftplib

def main():

    # Get disk name (e.g. HOLO-02). Don't need entire path. Get email.
    disk = raw_input('Input disk name (e.g. HOLO-02):')
    print disk
    email = raw_input('Input email address to send results:')

    # Hardcode path and ftp site
    disk_data_dir =  '/run/media/ads/' + disk + '/holodec'
    ftp_site = 'ftp.eol.ucar.edu'
    ftp_data_dir = 'pub/data/incoming/spicule/EOL_data/holodec'

    # ftp files from disk_data_dir to ftp_site:ftp_data_dir
    # will end out in /net/ftp/<ftp_data_dir>
    try:
        print 'Opening connection to ftp.eol.ucar.edu'
        ftp = ftplib.FTP(ftp_site)
        ftp.login("anonymous", email)
        ftp.cwd(ftp_data_dir)
    except ftplib.all_errors as e:
        print 'Error connecting to FTP site: ' + e
        ftp.quit()

    print "Putting files: "
    for file_name in os.listdir(disk_data_dir):
        print disk_data_dir + '/' + file_name
        try:
            file = open(disk_data_dir + '/' + file_name, 'r')
            ftp.storbinary('STOR ' + file_name, file)
            file.close()
        except ftplib.all_errors as e:
            print 'Error writing '+file_name+' to '+ ftp_site+':/'+ftp_data_dir
            print e
        

    ftp.quit()


if __name__ == "__main__":
    main()
