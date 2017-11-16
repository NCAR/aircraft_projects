Name: raf-gv
Version: 1.0
Release: 17
Summary: Metapackage for all server and satcom packages needed on GV

License: GPL
Source: %{name}-%{version}.tar.gz

Requires: raf-server-common
Requires: raf-ac-firewall
Requires: raf-gv-dhcp
Requires: raf-ac-named
Requires: raf-gv-ddclient
Requires: raf-satcom
#Requires: raf-satcom-bgan
Requires: raf-ac-nfs
Requires: raf-ac-avaps
Requires: raf-ac-mtp
Requires: raf-www-map
Requires: raf-www-control
Requires: raf-www-camera
Requires: squid
Requires: libdc1394-devel

BuildArch: noarch

%description
Metapackage for all server and satcom packages needed on GV.

%prep
%setup -q -n raf-server-common


%install
mkdir -p ${RPM_BUILD_ROOT}/var/spool/cron/ads
mkdir -p ${RPM_BUILD_ROOT}/home/ads/Desktop
cp var/spool/cron/crontab.ads.gv	${RPM_BUILD_ROOT}/var/spool/cron/ads
cp home/ads/Desktop/*			${RPM_BUILD_ROOT}/home/ads/Desktop
cp -r home/ads/.subversion		${RPM_BUILD_ROOT}/home/ads


%post
echo "export AIRCRAFT=GV_N677F" > /etc/profile.d/ads3.sh
sed -i '/^IPADDR=.*/IPADDR=128.117.44.102/' /etc/sysconfig/network-scripts/ifcfg-em3


%files
%config %attr(0600,ads,ads) /var/spool/cron/ads
%config %attr(0640,ads,ads) /home/ads/.subversion/servers
%attr(0755,ads,ads) /home/ads/Desktop/start_camera.desktop
%attr(0755,ads,ads) /home/ads/Desktop/start_mpds.desktop
%attr(0755,ads,ads) /home/ads/Desktop/start_iridium_tbal.desktop
%attr(0755,ads,ads) /home/ads/Desktop/start_iridium_blue.desktop
%attr(0755,ads,ads) /home/ads/Desktop/stop_camera.desktop
%attr(0755,ads,ads) /home/ads/Desktop/stop_mpds.desktop
%attr(0755,ads,ads) /home/ads/Desktop/stop_iridium.desktop


%changelog
* Thu Nov 16 2017 Erik Johnson <ej@ucar.edu> 1.0-18
- move catalog-related crontab entries from ads user to catalog user
- rename crontabs from crontab.ads.<plane> to ads.<plane>.crontab
* Tue Sep 19 2017 Chris Webster <cjw@ucar.edu> 1.0-16
- Addition of raf-server-common to consolidate common config between lab and ac servers.
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
- Added raf-ads3-rsyncd
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- Added raf-gv-ddclient
* Fri Apr 4 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- Initial hack
