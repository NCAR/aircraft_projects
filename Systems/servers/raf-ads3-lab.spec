Summary: Metapackage for all server and satcom packages needed on lab systems.
Name: raf-ads3-lab
Version: 1.0
Release: 5
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-ads-user
Requires: raf-lab-dhcp
Requires: raf-lab-named
Requires: raf-lab-ntp
Requires: ael-local-dpkgs
Requires: raf-ads3-sudoers

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on lab systems.

%files 

%changelog
* Wed Nov 24 2009 John Wasinger <wasinger@ucar.edu> 1.0-5
- Added raf-ads-user
* Fri Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Added raf-ads3-sudoers
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added ael-local-dpkgs, remove raf-ads3-rsyncd
* Thu Nov 20 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added rad-ads3-rsyncd
* Tue Oct 24 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial
