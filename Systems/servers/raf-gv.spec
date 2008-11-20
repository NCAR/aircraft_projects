Summary: Metapackage for all server and satcom packages needed on GV
Name: raf-gv
Version: 1.0
Release: 3
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-ac-ntp
Requires: raf-ac-firewall
Requires: raf-gv-dhcp
Requires: raf-ac-named
Requires: raf-gv-ddclient
Requires: raf-satcom
Requires: raf-ads3-rsyncd

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on GV.

%files 

%changelog
* Thu Nov 20 2008 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added rad-ads3-rsyncd
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added raf-gv-ddclient
* Fri Apr 4 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- Initial hack
