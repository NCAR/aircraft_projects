Name: raf-eol-rt-data
Version: 1.0
Release: 1
Summary: Metapackage for requirements specific to eol-rt-data ground server.
Source: %{name}-%{version}.tar.gz
License: GPL

Requires: raf-ac-postgresql
Requires: scons
Requires: qt-devel
Requires: nidas
Requires: nidas-devel
Requires: python-devel
Requires: openssl-devel
Requires: bzip2-devel

BuildArch: noarch

%description
   Additional configuration of postgresql for RAF ground stations. To be 
installed after raf-ac-postgresql is installed.
  - install raf-ac-postgresql if not already installed
    - yum install will install missing dependencies
    - rpm -ivh install requires dependencies to be listed on the command line
      or already installed.
  - install other dependencies
  - create platforms database and aircraft-specific databases
  - install crontab in /var/spool/cron/ads so will run as ads user on eol-rt-data

%prep
%setup -q -n %{name}

%pre
/usr/bin/timedatectl set-timezone UTC

%install
cp -r var %{buildroot}/

%post
# Platforms database holds a list of all aircraft we support. Need one DB 
# per aircraft.
createdb -U postgres platforms
createdb -U postgres real-time-A10
createdb -U postgres real-time-B146
createdb -U postgres real-time-C130
createdb -U postgres real-time-DC8
createdb -U postgres real-time-DLR
createdb -U postgres real-time-GH
createdb -U postgres real-time-GV
createdb -U postgres real-time-N42RF
createdb -U postgres real-time-N43RF
createdb -U postgres real-time-N49RF
createdb -U postgres real-time-WB57
createdb -U postgres real-time-WKA


%clean
rm -rf %{buildroot}

%files
%defattr(-,postgres,postgres)
%config /var/spool/cron/ads

%changelog
* Fri Jul 28 2017 Janine Aquino <janine@ucar.edu> 1.0-2
- Install crontab
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Initial hack
