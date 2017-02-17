Name: raf-ac-mtp
Version: 1 
Release: 2
Summary: Spec file for MTP instrument

License: none
Distribution: RHEL 7.3 Linux
BuildArch: noarch

Requires: raf-ads-user
Requires: vsftpd python-inotify

%description
Setup for receiving MTP data from the mtp-pc.

%prep

%build

%install
mkdir -p ${RPM_BUILD_ROOT}/var/r1/mtp
mkdir -p ${RPM_BUILD_ROOT}/var/www/html/mtp

%post
%if 0%{?rhel} < 7
/sbin/chkconfig --level 345 vsftpd on
%else
/bin/systemctl enable vsftpd
$endif

echo "*/3 * * * * /home/local/Systems/scripts/send_MTP.cron > /tmp/send_mtp.log 2>&1" >> /var/spool/cron/ads

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,ads,ads)
/var/r1/mtp
/var/www/html/mtp

%changelog
* Wed Feb 1 2017 <cjw@ucar.edu> 1-2
- Updates for rhel 7
* Sat Aug 7 2010 <cjw@ucar.edu> 1-1
- created initial package 
