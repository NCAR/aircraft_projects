Summary: Metapackage for all server and satcom packages needed on GV
Name: raf-ads3-lab
Version: 1.0
Release: 1
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-lab-dhcp
Requires: raf-lab-named
Requires: raf-lab-ntp

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on lab systems.

%files 

%changelog
* Tue Oct 24 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial
