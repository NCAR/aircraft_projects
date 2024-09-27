"Utility class to download images and kml files."

import sys
import time
import os
import iss.time_tools as tt
from raf.datepattern import DatePattern
import raf.singleton as singleton
import raf.config
import shutil
import logging

logger = logging.getLogger(__name__)

class Downloader(object):

    def __init__(self):
        self.local_dir = '/var/www/html/flight_data/GE/'
        self.file_pattern = None
        self.file_type = None
        self.latest_file_name = None
        self.num_files_to_get = 1
        self.label = None
        self.ftp_dir = None
        self.begin = None
        self.end = None
        self.ftp = None

    def setFtp(self, ftp):
        self.ftp = ftp

    def setLocalDirectory(self, local_dir):
        self.local_dir = local_dir

    def setNumFiles(self, num):
        self.num_files_to_get = num

    def setLatestFileName(self, name):
        self.latest_file_name = name

    def localListing(self):
        return os.listdir(self.local_dir)

    def setFiles(self, file_type, file_pattern):
        self.file_type = file_type
        self.file_pattern = file_pattern

    def setFtpDirectory(self, ftp_dir):
        self.ftp_dir = ftp_dir

    def setTimeRange(self, begin, end):
        self.begin = begin
        self.end = end

    def setTimespan(self, timespan):
        "Set time range using a special string syntax."
        trange = tt.parseTimespan(timespan)
        if not trange[1]:
            trange[1] = time.time()
        self.setTimeRange(trange[0], trange[1])

    def remoteListing(self):
        self.ftp.open()
        # Generate the patterns we want to select, then accumulate them all
        # into one listing, sorted lexically assuming that also sorts by
        # time.
        dp = DatePattern(self.file_pattern)
        globs = dp.generate(self.begin, self.end)
        listing = self.ftp.listDirectory(self.ftp_dir, globs=globs)
        logger.info("%d %s files found for time range %s to %s" %
                    (len(listing), self.file_type, 
                     tt.formatTime(self.begin), tt.formatTime(self.end)))
        listing = self.ftp.sortListing(listing)
        return listing

    def downloadEntry(self, entry):
        return self.download(entry.path)

    def download(self, path):
        self.ftp.open()
        localpath = os.path.join(self.local_dir, os.path.basename(path))
        self.ftp.download(path, localpath)
        return localpath

    def installLatest(self, localpath, destpath, transform=None):
        """
        Install local file as the new latest file for some file type.

        If transform is given, then pass each line into the function and
        write the result to the destination file.  Otherwise use a straight
        copy.
        """
        destdir = os.path.dirname(os.path.abspath(destpath))
        if not os.path.isdir(destdir):
            logger.info("Skipping install of %s because %s does not exist.",
                        destpath, destdir)
            return
        if transform:
            with open(localpath, "r") as src:
                with open(destpath, "w") as dest:
                    lines = src.readlines()
                    if transform:
                        lines = [transform(line) for line in lines]
                    dest.writelines(lines)
        else:
            shutil.copyfile(localpath, destpath)
        logger.info("%s copied to %s.", localpath, destpath)

    def run(self, args):
        config = raf.config.Config()
        config.parseArgs(args)
        config.setupLogging()
        if config.has_key('local_dir'):
            self.setLocalDirectory(config['local_dir'])
        if config.has_key('ftp_dir'):
            self.setFtpDirectory(config['ftp_dir'])
        self.setFtp(config.FTP())

        # Limit to running a single instance of this script.
        sp = singleton.SingleProcess(self.file_type).try_lock()
        sp.lock_or_fail()
        logger.info("Starting downloader for %s files.", self.file_type)

        # List the files already in the local directory
        listing = self.localListing()
        ftplist = self.remoteListing()
        if not ftplist:
            print("No files found on ftp server.")
            sys.exit(1)

        latest = ftplist[-1]
        print("Latest file on ftp site: %s" % (latest.filename()))

        # Check to see if we've got the most recent file
        if latest.filename() in listing:
            print("Already have file %s" % (latest.filename()))
            sys.exit(0)

        localpath = self.download(latest.path)
        if self.latest_file_name:
            self.installLatest(localpath, 
                               os.path.join(self.local_dir, 
                                            self.latest_file_name))
        print("Done.")

        
def main():
    _pattern = 'satellite.GOES-13.%Y%m%d%H%M.*thermal-IR.jpg'
    dld = Downloader()
    cfg = raf.config.Config()
    cfg.parseArgs(["--debug"])
    cfg.setupLogging()
    cfg.ftp_site = 'ftp.eol.ucar.edu'
    dld.setFtp(cfg.FTP())
    dld.setFiles('IR', _pattern)
    dld.setFtpDirectory('/pub/archive/projects/tests/ORCAS')
    begin = tt.parseTime('201601181400')
    end = tt.parseTime('201601190259')
    dld.setTimeRange(begin, end)
    listing = dld.remoteListing()
    for de in listing:
        print(de.path)


if __name__ == "__main__":
    main()

