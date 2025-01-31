
from raf.downloader import Downloader
import iss.time_tools as tt
import raf.config as config
import os
import re
import pytest


_pattern = 'satellite.GOES-13.%Y%m%d*thermal-IR.jpg'


@pytest.fixture
def dld():
    dld = Downloader()
    cfg = config.Config()
    cfg.parseArgs(["--debug"])
    cfg.setupLogging()
    cfg.ftp_site = 'ftp.eol.ucar.edu'
    dld.setFtp(cfg.FTP())
    dld.setFiles('IR', _pattern)
    dld.setFtpDirectory('/pub/archive/projects/tests/ORCAS')
    begin = tt.parseTime('201601181400')
    end = tt.parseTime('201601190259')
    dld.setTimeRange(begin, end)
    return dld

def test_downloader(dld):
    assert dld.file_pattern == _pattern
    assert dld.file_type == 'IR'
    assert dld.ftp_dir == '/pub/archive/projects/tests/ORCAS'
    assert dld.ftp.host == 'ftp.eol.ucar.edu'
    assert dld.begin == tt.parseTime('201601181400')
    assert dld.end == tt.parseTime('201601190259')


@pytest.mark.slowtest
def test_remote_listing(dld, tmpdir):
    (begin, end) = (dld.begin, dld.end)
    dld.setTimeRange(begin - 48*3600, end - 48*3600)
    listing = dld.remoteListing()
    assert not listing
    dld.setTimeRange(begin, end)
    listing = dld.remoteListing()
    for de in listing:
        print(de.path)
    assert listing
    assert listing[-1].path.endswith('IR.jpg')
    assert listing[0] <= listing[-1]
    latest = listing[-1]
    print("downloading %s..." % (latest.path))
    dld.setLocalDirectory(str(tmpdir))
    npath = dld.download(latest.path)
    xpath = tmpdir.join(os.path.basename(latest.path))
    assert npath == str(xpath)
    assert xpath.exists()
    assert xpath.size() > 0

_source = """
<Style>
<IconStyle>
<color>5014F064</color>
<scale>4</scale>
<heading>0</heading>
<Icon>
<href>http://www.nrlmry.navy.mil/TC/kml/TC/images/windbarbs/000/wb_000_320.png</href>
</Icon>
<gx:headingMode>worldNorth</gx:headingMode>
</IconStyle>
</Style>
<description><![CDATA[<p><b>CDPHE Station: 080310027</b></p> Observations on 20140729 at 1908</p> <p>Ozone  ppm </b></p> <br><p> PM2.5  microg/m3</p> <p> Wind Direction: 320.889825</p> deg <p>Wind Speed: 4.59075927 knots</b><br>]]></description>
"""

_transformed = """
<Style>
<IconStyle>
<color>5014F064</color>
<scale>4</scale>
<heading>0</heading>
<Icon>
<href>http://acserver.raf.ucar.edu/flight_data/display/windbarbs/000/wb_000_320.png</href>
</Icon>
<gx:headingMode>worldNorth</gx:headingMode>
</IconStyle>
</Style>
<description><![CDATA[<p><b>CDPHE Station: 080310027</b></p> Observations on 20140729 at 1908</p> <p>Ozone  ppm </b></p> <br><p> PM2.5  microg/m3</p> <p> Wind Direction: 320.889825</p> deg <p>Wind Speed: 4.59075927 knots</b><br>]]></description>
"""


def test_transform(dld, tmpdir):
    spath = tmpdir.join("source.txt")
    spath.write(_source)
    rx = re.compile(r'www\.nrlmry\.navy\.mil/TC/kml/TC/images')
    dpath = tmpdir.join("latest.txt")
    dld.installLatest(str(spath), str(dpath), transform=lambda line: 
                      rx.sub(r'acserver.raf.ucar.edu/flight_data/display',
                             line))
    transformed = dpath.read()
    assert transformed == _transformed

