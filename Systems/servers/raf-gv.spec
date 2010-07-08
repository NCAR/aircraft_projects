Summary: Metapackage for all server and satcom packages needed on GV
Name: raf-gv
Version: 1.0
Release: 9
License: GPL
Group: System Environment

Requires: raf-ads3-syslog
Requires: raf-ads3-systl
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
Requires: nidas
Requires: nidas-x86-build
Requires: ael-local-dpkgs

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on GV.

%files 

%changelog
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
