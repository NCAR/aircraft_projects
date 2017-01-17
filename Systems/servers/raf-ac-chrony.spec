Name: raf-ac-chrony
Version: 1.0
Release: 1
Summary: Configuration for chrony on RAF aircraft and labs.

License: GPL
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: chrony

%description
Configuration for chrony (NTP client replacement) on RAF ADS3 lab (non-aircraft) server systems

%prep

%build

%install
rm -fr $RPM_BUILD_ROOT

%triggerin -- chrony
# triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

cf=/etc/chrony.conf
if grep -q "centos.pool" $cf; then
  sed -i -c '/^server/d' $cf
  sed -i -c '3 a server 192.168.184.10 iburst\nallow 192.168\nbroadcast 30 192.168.84.255\nbroadcast 30 192.168.184.255\n' $cf
fi

/bin/systemctl enable chronyd.service
/bin/systemctl restart chronyd.service


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%changelog
* Wed Apr 20 2016 Chris Webster <cjw@ucar.edu>
- initial version
