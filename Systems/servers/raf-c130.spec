Summary: Metapackage for all server and satcom packages needed on C130
Name: raf-c130
Version: 1.0
Release: 1
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-ac-ntp
Requires: raf-ac-firewall
Requires: raf-c130-dhcp
Requires: raf-ac-named
Requires: raf-satcom

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on GV.

%files 

%changelog
* Fri Apr 4 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- Initial hack
