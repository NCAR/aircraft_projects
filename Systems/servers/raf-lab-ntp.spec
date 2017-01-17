Name: raf-lab-ntp
Version: 1.0
Release: 4
Summary: Configuration for NTP on RAF ADS3 lab (non-aircraft) server systems

License: GPL
Packager: Gordon Maclean <maclean@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: ntp
Requires: nidas-buildeol

%description
Configuration for NTP on RAF ADS3 lab (non-aircraft) server systems

%prep

%build

%install
rm -fr $RPM_BUILD_ROOT
%triggerin -- ntp
# %%triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# Lab systems are broadcastclients, allow query from 192.168.0.0
cf=/etc/ntp.conf
if ! grep -q "^[[:space:]]*broadcastclient" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
abroadcastclient
arestrict 192.168.0.0 mask 255.255.0.0 nomodify notrap
a###### end %{name}-%{version} ######
}' $cf
fi
if ! grep -q "^[[:space:]]*restrict 192.168.0.0" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
arestrict 192.168.0.0 mask 255.255.0.0 nomodify notrap
a###### end %{name}-%{version} ######
}' $cf
fi

cf=/etc/ntp/step-tickers
if ! grep -q "^[[:space:]]*128.117" $cf && \
    ! grep -q "^[[:space:]]*.ucar.edu" $cf; then
    echo "syrah.eol.ucar.edu" > $cf
fi

if ! { chkconfig --list ntpd | grep -q "5:on"; }; then
    chkconfig --level 2345 ntpd on
fi
/etc/init.d/ntpd restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%changelog
* Sat Apr  7 2012 John Wasinger <wasinger@ucar.edu> 1.0-4
- Updated Requires for nidas packages.
* Tue Dec 15 2009 John Wasinger <wasinger@ucar.edu>
- s/atd/eol/g
* Fri Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
