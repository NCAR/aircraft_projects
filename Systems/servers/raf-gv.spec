Name: raf-gv
Version: 1.0
Release: 16
Summary: Metapackage for all server and satcom packages needed on GV

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
Requires: raf-gv-dhcp
Requires: raf-ac-named
Requires: raf-gv-ddclient
Requires: raf-satcom
#Requires: raf-satcom-bgan
Requires: raf-ads3-sudoers
Requires: raf-ac-nfs
Requires: raf-ac-postgresql
Requires: raf-ac-avaps
Requires: raf-ac-mtp
Requires: raf-www-control
Requires: raf-www-camera
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
Metapackage for all server and satcom packages needed on GV.

%pre
/usr/bin/timedatectl set-timezone UTC

dir=/home/local
if [ ! -d $dir ]; then
  mkdir -p $dir/bin $dir/include $dir/lib
  chown -R ads:ads $dir
  chmod g+w $dir/bin $dir/include $dir/lib
  ln -s $dir /opt/local
fi

mkdir -p /home/data
mkdir -p /var/r1
mkdir -p /var/r2
chown ads:ads /home/data /var/r1 /var/r2


%post

/usr/bin/hostnamectl set-hostname acserver.raf.ucar.edu

cf=/etc/rc.local
if ! grep -q "nimbus.pid" $cf; then
  cat << EO_RC_LOCAL >> $cf

# Perform some basic housekeeping / clean up.
rm -f /tmp/nimbus.pid
rm -f /home/DataBases/postmaster.pid

EO_RC_LOCAL

fi


cf=/etc/hosts.allow
if ! grep -q "128.117" $cf; then
  cat << EO_HOSTS_ALLOW >> $cf
ALL : LOCAL, .ucar.edu, 128.117., 127.0.0.1, 192.168.
EO_HOSTS_ALLOW
fi


sed '/^export AIRCRAFT/c\export AIRCRAFT=GV_N677F' ads3_environment.sh


%files 


%changelog
* Mon Jan 16 2017 Chris Webster <cjw@ucar.edu> 1.0-15
- Change raf-ac-ntp to raf-ac-chrony for RHEL7.  Add gdm and selinux.
* Tue Apr 5 2016 Chris Webster <cjw@ucar.edu> 1.0-14
- Change raf-ac-ntp to raf-ac-chrony for RHEL7.  Add gdm and selinux.
* Wed Nov 4 2015 Chris Webster <cjw@ucar.edu> 1.0-14
- Updated Requires kde-baseapps (kdialog).
* Thu May 16 2013 Chris Webster <cjw@ucar.edu> 1.0-13
- Updated Requires for new packages.
* Sat Apr  7 2012 Gordon Maclean <maclean@ucar.edu> 1.0-12
- Updated Requires for new nidas packages.
* Fri Aug 5 2011 Chris Webster <cjw@ucar.edu> 1.0-11
- Add raf-ac-nfs package. Added GMT.
* Mon Feb 21 2011 Gordon Maclean <maclean@ucar.edu> 1.0-11
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
