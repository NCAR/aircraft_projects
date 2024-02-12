##Class for FieldData to inherit all the constants

class FileExts:
    CONFIG_EXT= {"LRT": "", "HRT": "h", "SRT": "s"}
    FILE_TYPE = {
                "ADS": "",
                "LRT": "",
                "KML": "",
                "HRT": "h",
                "SRT": "s",
                "ICARTT": "",
                "IWG1": "",
                "PMS2D": "",
                }
    RATE = {
        "LRT": "1",
        "HRT": "25",
        "SRT": "0",
    }
class Directories:
    ZIP_DIR = '/tmp/'
    QC_FTP_SITE = 'catalog.eol.ucar.edu'


class ConstantsManagement:
    def __init__(self):
        # Set constants from separate classes as attributes
        for cls in [FileExts, StatusConst]:
            for key, value in cls.__dict__.items():
                if not key.startswith("__"):
                    self.__dict__.update(**{key: value})

    def __setattr__(self, name, value):
        raise TypeError("Constants are immutable")