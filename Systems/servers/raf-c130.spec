Name: raf-c130
Version: 1.0
Release: 15
Summary: Metapackage for all server and satcom packages needed on C130

License: GPL

Requires: raf-devel
Requires: raf-ads3-syslog
Requires: raf-ads3-sysctl
Requires: raf-ads-user
Requires: raf-ac-gdm
Requires: raf-ac-selinux
Requires: raf-ac-chrony
Requires: raf-ac-nagios
Requires: raf-ac-firewall
Requires: raf-c130-dhcp
Requires: raf-ac-named
Requires: raf-c130-ddclient
Requires: raf-satcom
Requires: raf-satcom-bgan
Requires: raf-ads3-sudoers
Requires: raf-ac-nfs
Requires: raf-ac-avaps
Requires: raf-www-control
Requires: raf-www-camera
Requires: raf-postgresql
Requires: GMT
Requires: ruby
Requires: squid
Requires: libdc1394-devel
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
Requires: nagircbot

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on C130.

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
* Mon Jan 16 2017 Chris Webster <cjw@ucar.edu> 1.0-15
- Change raf-ac-ntp to raf-ac-chrony for RHEL7.  Add gdm and selinux.
* Tue Apr 5 2016 Chris Webster <cjw@ucar.edu> 1.0-14
- Change raf-ac-ntp to raf-ac-chrony for RHEL7 migration.  Add gdm & selinux.
* Tue Nov 3 2015 Chris Webster <cjw@ucar.edu> 1.0-14
- Updated Requires kde-baseapps (kdialog).
* Thu May 16 2013 Chris Webster <cjw@ucar.edu> 1.0-13
- Updated Requires for new packages.
* Sat Apr  7 2012 Gordon Maclean <maclean@ucar.edu> 1.0-12
- Updated Requires for new nidas packages.
* Fri Aug 5 2011 Chris Webster <cjw@ucar.edu> 1.0-11
- Add raf-ac-nfs package.  Added GMT.
* Wed Feb 23 2011 Gordon Maclean <maclean@ucar.edu> 1.0-11
- Added Requires: nidas-ael (cross compiling) and nidas-daq (udev rules)
* Tue Jul 13 2010 Gordon Maclean <maclean@ucar.edu> 1.0-10
- Added Requires: chrony
* Thu Jul 08 2010 Chris Webster <cjw@ucar.edu> 1.0-9
- Added raf-ads3-sysctl
* Sat Jan 23 2010 Gordon Maclean <maclean@ucar.edu> 1.0-7
- Added raf-satcom-bgan
* Wed Jan 06 2010 Chris Webster <cjw@ucar.edu> 1.0-6
- Added raf-ads-user
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-5
- Added raf-ads3-sudoers
* Mon Nov 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Added ael-local-dpkgs, remove raf-ads3-rsyncd
* Thu Nov 20 2008 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added rad-ads3-rsyncd
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added raf-c130-ddclient
* Fri Apr 4 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- Initial hack
