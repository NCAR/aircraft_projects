Summary: Metapackage for all server and satcom packages needed on GV
Name: raf-ads3-lab
Version: 1.0
Release: 3
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-lab-dhcp
Requires: raf-lab-named
Requires: raf-lab-ntp
Obsoletes: raf-ads3-rsyncd
Requires: ael-local-dpkgs

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on lab systems.

%files 

%changelog
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added ael-local-dpkgs, remove raf-ads3-rsyncd
* Thu Nov 20 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added rad-ads3-rsyncd
* Tue Oct 24 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial
