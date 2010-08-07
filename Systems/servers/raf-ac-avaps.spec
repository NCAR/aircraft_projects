Summary: Setup acserver for AVAPS.
Name: raf-ac-avaps
Version: 1
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
BuildRoot: %{_tmppath}/%{name}-root
Vendor: UCAR
BuildArch: noarch
Requires: rsync crontabs
#Source: %{name}-%{version}.tar.gz

%description
Setup for AVAPS dropsonde data collection:
  - allow rsync in from avaps computer
  - cron entry 
  - script that cron entry runs to check for new files and ftp them out.


%prep
# %setup -n %{name}

%build

%install
mkdir -p ${RPM_BUILD_ROOT}/mnt/r1/dropsondes
mkdir -p ${RPM_BUILD_ROOT}/var/www/html/skewT

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
/var/www/html/skewT

%changelog
* Sat Aug 7 2010 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version; AVAPS
