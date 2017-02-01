Name: raf-ac-avaps
Version: 1
Release: 2
Summary: Setup acserver for AVAPS.

License: GPL
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: raf-ads-user
Requires: rsync crontabs python-inotify

%description
Setup for AVAPS dropsonde data collection:
  - allow rsync in from avaps computer
  - cron entry 
  - script that cron entry runs to check for new files and ftp them out.

AVAPS process works as follows.  The AVAPS computer rsync's D-files to our computer
after a drop in /mnt/r1/dropsondes.  The cron entry to run send_avaps.cron.py runs
and ftp's the file to the ground, runs Aspen to produce a Skewt which is placed in
/var/www/html/skewt.

%prep

%build

%install
mkdir -p ${RPM_BUILD_ROOT}/mnt/r1/dropsondes/tmp
mkdir -p ${RPM_BUILD_ROOT}/var/www/html/skewt

%post

echo "*/2 * * * * /home/local/Systems/scripts/send_avaps.cron.py 2>&1 /tmp/send_avaps.log" >> /var/spool/cron/ads


%triggerin -- rsync
cf=/etc/rsyncd.conf
if [ -f $cf ]; then
    cat >> $cf << EOD
# suppress log messages
log file = /dev/null

[dropsondes]
    comment = Dropsonde delivery folder
    path = /mnt/r1/dropsondes
    uid = ads
    gid = ads
    read only = no
    use chroot = false
    hosts allow = 127.0.0.1 192.168.0.0/16
EOD
fi

%files
%defattr(-,ads,ads)
/mnt/r1/dropsondes
/var/www/html/skewt

%changelog
* Wed Feb 1 2017 Chris Webster <cjw@ucar.edu> - 1.0-2
- Add requires ads-user package...since we do chown.
* Sat Aug 7 2010 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version; AVAPS
