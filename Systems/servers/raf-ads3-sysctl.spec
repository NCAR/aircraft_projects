Name: raf-ads3-sysctl
Version: 1.1
Release: 0
Summary: sysctl.d

License: GPL
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
Source: %{name}-%{version}.tar.gz
BuildArch: noarch

%description
Modify sysctl.conf to engage IP forwarding, and allow Alt + SysRq + B to reboot the computer.

%prep
%setup -q -n %{name}


%install
mkdir -p ${RPM_BUILD_ROOT}/etc/sysctl.d
cp etc/sysctl.d/90-override.conf ${RPM_BUILD_ROOT}/etc/sysctl.d


%files
%config %attr(0755,root,root) /etc/sysctl.d/90-override.conf


%changelog
* Tue Feb 20 2018 Chris Webster <cjw@ucar.edu> - 1.1
- Migrate to RHEL 7.  Use /etc/sysctl.d/90-override.conf
* Wed Jul 03 2013 Chris Webster <cjw@ucar.edu> - 1.0-3
- Clean up logrotate.d/ads3 file.  Bugs.
* Mon Feb 21 2011 Gordon Maclean <maclean@ucar.edu> - 1.0-2
- /etc/sysctl.conf is owned by initscripts, can't be owned by this package.
* Sat Feb 06 2010 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
- make sure ip forwarding is on
- turn on kernel sysreq, compuer rebooting with Alt + SysRq + B
