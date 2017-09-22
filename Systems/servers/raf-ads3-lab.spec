Name: raf-ads3-lab
Summary: Metapackage for all server and satcom packages needed on lab systems.
Version: 1.0
Release: 10
License: GPL

Requires: raf-server-common
Requires: eol-devel
Requires: raf-devel
Requires: raf-lab-dhcp
Requires: raf-lab-named

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on lab systems.


%pre

echo "export AIRCRAFT=Lab_N600" > /etc/profile.d/ads3.sh

%files 

%changelog
* Tue Sep 19 2017 Chris Webster <cjw@ucar.edu> 1.0-10
- Addition of raf-server-common.
* Mon Jan 16 2017 Chris Webster <cjw@ucar.edu> 1.0-9
- Updates for RHEL7.
- Addition of raf-devel.
* Mon Apr 11 2016 Chris Webster <cjw@ucar.edu> 1.0-8
- Change raf-ac-ntp to raf-ac-chrony for RHEL7 migration.
- add raf-ac-gdm : auto-login.
- add raf-ac-selinux : disable
- Require eol-devel, postgresql-server.
- Create some /home/local/ directories
- Check out subversion items.
* Wed Nov 4 2015 Chris Webster <cjw@ucar.edu> 1.0-7
- Added Requires: minicom & kde-baseapps
* Tue Jul 13 2010 Gordon Maclean <maclean@ucar.edu> 1.0-6
- Added Requires: chrony
* Tue Nov 24 2009 John Wasinger <wasinger@ucar.edu> 1.0-5
- Added raf-ads-user
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Added raf-ads3-sudoers
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added ael-local-dpkgs, remove raf-ads3-rsyncd
* Thu Nov 20 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added rad-ads3-rsyncd
* Fri Oct 24 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial
