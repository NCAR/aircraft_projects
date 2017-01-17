Summary: Metapackage for all server and satcom packages needed on lab systems.
Name: raf-ads3-lab
Version: 1.0
Release: 9
License: GPL
Group: System Environment

Requires: eol-devel
Requires: raf-devel
Requires: raf-ads3-syslog
Requires: raf-ads-user
Requires: raf-ac-gdm
Requires: raf-ac-selinux
Requires: raf-ac-chrony
Requires: raf-ac-nagios
Requires: raf-lab-dhcp
Requires: raf-lab-named
Requires: raf-ads3-sudoers
Requires: raf-www-control
Requires: raf-postgresql
Requires: GMT
Requires: postgresql-server
Requires: kde-baseapps
Requires: nidas-min
Requires: nidas-libs
Requires: nidas-modules
Requires: nidas-autocal
Requires: nidas-configedit
Requires: nidas-daq
Requires: nidas-devel
Requires: nidas-build
Requires: nidas-buildeol
Requires: nidas-ael
Requires: ael-local-dpkgs

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on lab systems.


%pre
dir=/home/local
if [ ! -d $dir ]; then
  mkdir -p $dir/bin $dir/include $dir/lib
  chown -R ads:ads $dir
  chmod g+w $dir/bin $dir/include $dir/lib
  ln -s $dir /opt/local
fi

dir=/home/data
if [ ! -d $dir ]; then
  mkdir -p $dir
fi

%files 

%changelog
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
