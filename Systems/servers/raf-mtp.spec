Summary: Spec file for MTP instrument
Name: raf-mtp
Version: 1 
Release: 1
Group: Applications/Engineering
#Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: vsftpd
# BuildRoot is only needed by older rpm versions
BuildRoot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
Setup for receiving MTP data from the mtp-pc.

%prep
# %setup -n raf-mtp

%build

%install
mkdir -p ${RPM_BUILD_ROOT}/mnt/r1/mtp
mkdir -p ${RPM_BUILD_ROOT}/var/www/html/mtp

%post
/sbin/chkconfig --level 345 vsftpd on

echo "*/3 * * * * /home/local/Systems/scripts/send_MTP.cron > /tmp/send_mtp.log 2>&1" >> /var/spool/cron/ads

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,ads,ads)
/mnt/r1/mtp
/var/www/html/mtp

%changelog
* Sat Aug 7 2010 <cjw@ucar.edu> 1-1
- created initial package 
