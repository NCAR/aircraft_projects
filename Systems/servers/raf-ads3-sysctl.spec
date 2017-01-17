Name: raf-ads3-sysctl
Version: 1.0
Release: 3
Summary: triggerin script for sysctl.conf

License: GPL
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: initscripts

%description
Modify sysctl.conf to engage IP forwarding, and allow Alt + SysRq + B to reboot the computer.


%triggerin -- initscripts
cf=/etc/sysctl.conf

if grep -q "net.ipv4.ip_forward = 0" $cf || grep -q "kernel.sysrq = 0" $cf 
then
  /bin/cp $cf /etc/sysctl.rpmsave
  sed -i 's/net.ipv4.ip_forward = 0/net.ipv4.ip_forward = 1/g' $cf
  sed -i 's/kernel.sysrq = 0/kernel.sysrq = 1/g' $cf
fi


%files

%changelog
* Wed Jul 03 2013 Chris Webster <cjw@ucar.edu> - 1.0-3
- Clean up logrotate.d/ads3 file.  Bugs.
* Tue Feb 21 2011 Gordon Maclean <maclean@ucar.edu> - 1.0-2
- /etc/sysctl.conf is owned by initscripts, can't be owned by this package.
* Sun Feb 06 2010 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
- make sure ip forwarding is on
- turn on kernel sysreq, compuer rebooting with Alt + SysRq + B
