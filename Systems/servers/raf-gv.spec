Summary: Metapackage for all server and satcom packages needed on GV
Name: raf-gv
Version: 1.0
Release: 12
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-ads3-sysctl
Requires: raf-ads-user
Requires: raf-ac-ntp
Requires: raf-ac-nagios
Requires: raf-ac-firewall
Requires: raf-gv-dhcp
Requires: raf-ac-named
Requires: raf-gv-ddclient
Requires: raf-satcom
Requires: raf-satcom-mpds
Requires: raf-ads3-sudoers
Requires: nidas-buildeol
Requires: nidas-ael
Requires: nidas-daq
Requires: ael-local-dpkgs
Requires: chrony
Requires: raf-ac-nfs
Requires: raf-ac-avaps
Requires: raf-ac-mtp
Requires: GMT

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on GV.

%files 

%changelog
* Sat Apr  7 2012 Gordon Maclean <maclean@ucar.edu> 1.0-12
- Updated Requires for new nidas packages.
* Fri Aug 5 2011 Chris Webster <cjw@ucar.edu> 1.0-11
- Add raf-ac-nfs package. Added GMT.
* Wed Feb 21 2011 Gordon Maclean <maclean@ucar.edu> 1.0-11
- Added Requires: nidas-ael (cross compiling) and nidas-daq (udev rules)
* Tue Jul 13 2010 Gordon Maclean <maclean@ucar.edu> 1.0-10
- Added Requires: chrony
* Thu Jul 08 2010 Chris Webster <cjw@ucar.edu> 1.0-9
- Added raf-ads3-sysctl
* Sat Jan 23 2010 Gordon Maclean <maclean@ucar.edu> 1.0-7
- Added raf-satcom-mpds
* Wed Jan 06 2010 Chris Webster <cjw@ucar.edu> 1.0-6
- Added raf-ads-user
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-5
- Added raf-ads3-sudoers
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Added ael-local-dpkgs, remove raf-ads3-rsyncd
* Thu Nov 20 2008 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added rad-ads3-rsyncd
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added raf-gv-ddclient
* Fri Apr 4 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- Initial hack
