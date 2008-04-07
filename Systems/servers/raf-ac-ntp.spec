Summary: Configuration for NTP on RAF aircraft server systems
Name: raf-ac-ntp
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch
Requires: ntp
# Source: %{name}-%{version}.tar.gz

%description
Configuration for NTP on RAF aircraft server systems

%prep
# %setup -n %{name}

%build

%triggerin -- ntp
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# Lab systems are broadcastclients, allow query from 192.168.0.0
cf=/etc/ntp.conf
if ! egrep -q "^[[:space:]]*server[[:space:]]+timeserver" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
aserver timeserver
aserver tardis.ntp.ucar.edu
arestrict 192.168.0.0 mask 255.255.0.0 nomodify notrap
a###### end %{name}-%{version} ######
}' $cf
fi
if ! egrep -q "^[[:space:]]*restrict 192.168.0.0" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
arestrict 192.168.0.0 mask 255.255.0.0 nomodify notrap
a###### end %{name}-%{version} ######
}' $cf
fi

cf=/etc/ntp/step-tickers
if ! egrep -q "^[[:space:]]*192.168.184.10" $cf; then
    echo "192.168.184.10" > $cf
fi

if ! { chkconfig --list ntpd | fgrep -q "5:on"; }; then
    chkconfig --level 2345 ntpd on
fi
/etc/init.d/ntpd restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%changelog
* Sun Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
