Summary: triggerin script for sysctl.conf
Name: raf-ads3-sysctl
Version: 1.0
Release: 2
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
# becomes RPM_BUILD_ROOT
#BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Requires: initscripts
#Source: %{name}-%{version}.tar.gz

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
* Tue Feb 21 2011 Gordon Maclean <maclean@ucar.edu> - 1.0-2
- /etc/sysctl.conf is owned by initscripts, can't be owned by this package.
* Sun Feb 06 2010 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
- make sure ip forwarding is on
- turn on kernel sysreq, compuer rebooting with Alt + SysRq + B
