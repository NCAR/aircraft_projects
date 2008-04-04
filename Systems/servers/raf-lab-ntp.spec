Summary: Configuration for NTP on RAF ADS3 lab (non-aircraft) server systems
Name: raf-lab-ntp
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
Configuration for NTP on RAF ADS3 lab (non-aircraft) server systems

%prep
# %setup -n %{name}

%build

%triggerin -- ntp
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# Lab systems are broadcastclients, allow query from 192.168.0.0
cf=/etc/ntp.conf
if ! egrep -q "^[[:space:]]*broadcastclient" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
abroadcastclient
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
if ! egrep -q "^[[:space:]]*128.117" $cf && \
    ! egrep -q "^[[:space:]]*.ucar.edu" $cf; then
    echo "syrah.atd.ucar.edu" > $cf
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
