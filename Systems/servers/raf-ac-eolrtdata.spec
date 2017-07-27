Name: raf-ac-eolrtdata
Version: 1.0
Release: 1
Summary: Metapackage for requirements specific to eol-rt-data ground server.
License: GPL

Requires: raf-ac-postgresql

BuildArch: noarch

%description
   Additional configuration of postgresql for RAF ground stations. To be 
installed after raf-ac-postgresql is installed.
  - install raf-ac-postgresql if not already installed
    - yum install will install missing dependencies
    - rpm -ivh install requires dependencies to be listed on the command line
      or already installed.
  - create platforms database

%pre
/usr/bin/timedatectl set-timezone UTC


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
createdb -U postgres real-time-N42RF
createdb -U postgres real-time-N43RF
createdb -U postgres real-time-N49RF
createdb -U postgres real-time-WB57
createdb -U postgres real-time-WKA


%clean
rm -rf %{buildroot}

%files

%changelog
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Initial hack
