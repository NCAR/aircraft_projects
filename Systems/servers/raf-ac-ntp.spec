Name: raf-ac-ntp
Version: 1.0
Release: 3
Summary: Configuration for NTP on RAF aircraft server systems

License: GPL
Packager: Gordon Maclean <maclean@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: ntp

%description
Configuration for NTP on RAF aircraft server systems

%prep
# %setup -n %{name}

%build

%install
rm -fr $RPM_BUILD_ROOT

%triggerin -- ntp
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# Lab systems are broadcastclients, allow query from 192.168.0.0
cf=/etc/ntp.conf
if ! egrep -q "^[[:space:]]*server[[:space:]]+timeserver" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
# When not synced, poll every 2^4=16 seconds. Default minpoll is 2^6=64.
# After syncing, require ntpd to poll the timeserver at least every 2^6=64 seconds.
# The default maxpoll is 2^10=1024 secs.
aserver timeserver minpoll 4 maxpoll 6
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
* Tue Jan 31 2012 Tom Baltzer <tbaltzer@ucar.edu>
- remove tardis.ucar.edu - don't want to use it on the planes.
* Mon Mar 2 2010 Chris Webster <cjw@ucar.edu>
- Up version number for mod Gordon did to set minpoll and maxpoll
* Sun Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
