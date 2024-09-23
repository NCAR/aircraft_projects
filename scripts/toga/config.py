"Global configuration dictionary for RAF python utilities."

import os
import logging

logger = logging.getLogger(__name__)

import raf.rsync as rsync
import raf.ldm as ldm
import iss.eol_ftp as eol_ftp

class Config(dict):

    def __init__(self):
        self.loglevel = logging.INFO
        self.dryrun = False
        self.aircraft = None
        self.plane = None
        self.tail = None
        # ftp defaults
        self.ftp_site = 'catalog.eol.ucar.edu'
        self.ftp_login = 'anonymous'
        self.ftp_passwd = ''

    def addOptions(self, parser):
        parser.add_option("--debug", dest="loglevel", action="store_const",
                          const=logging.DEBUG, default=logging.ERROR,
                          help="Show debug log messages.")
        parser.add_option("--info", dest="loglevel", action="store_const",
                          const=logging.INFO, default=logging.ERROR,
                          help="Show info log messages.")
        parser.add_option("--dryrun", action="store_true", default=False,
                          help="Do not actually run commands.")
        parser.add_option("--localdir", type="string")
        return self

    def setOptions(self, options):
        self.dryrun = options.dryrun
        if options.localdir:
            self['local_dir'] = options.localdir
        self.loglevel = options.loglevel
        self.setupLogging()

    def parseArgs(self, argv):
        "Consume arguments which modify global configuration."
        i = 0
        while i < len(argv):
            arg = argv[i]
            if arg == "--debug":
                self.loglevel = logging.DEBUG
                del argv[i]
            elif arg == "--dryrun":
                self.dryrun = True
                del argv[i]
            elif arg == "--localdir":
                self['local_dir'] = argv[i+1]
                del argv[i:i+2]
            else:
                i += 1
        return argv

    def setupLogging(self):
        logging.basicConfig(level=self.loglevel)

    def setupAircraft(self):
        # Get information from AIRCRAFT environment variable
        if self.aircraft:
            return
        self.aircraft = os.environ.get('AIRCRAFT')
        if not self.aircraft:
            raise Exception("AIRCRAFT environment variable not defined!")
        self.plane, self.tail = self.aircraft.split("_", 1)

    def getPlane(self):
        self.setupAircraft()
        return self.plane

    def getCatalogIngestDir(self):
        return '/home/catalog/products/incoming/' + self.plane.lower()

    # Try a little dependency inversion and create the service objects from
    # Config factory methods, so the Config has a chance to modify the
    # objects according to the current configuration.

    def Rsync(self, *args):
        target = rsync.Rsync(*args)
        target.setDryrun(self.dryrun)
        return target

    def LDM(self, *args):
        target = ldm.LDM(*args)
        target.setDryrun(self.dryrun)
        return target

    def FTP(self, *args):
        "Use iss.eol_ftp.FtpDataServer pointed at ftp_site."
        target = eol_ftp.FtpDataServer(host=self.ftp_site, *args)
        target.setCredentials(self.ftp_login, self.ftp_passwd)
        return target
