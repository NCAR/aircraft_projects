Summary: Configuration for PPP over Iridium
Name: raf-satcom-iridium
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
# Requires: ppp >= 2.4.4

# LIC: GPL
%description
/etc files for configuring pppd over an Iridium connection

%prep
%setup -n %{name}

%build

%install
install -d $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig/networking/devices
install -d $RPM_BUILD_ROOT/etc/sysconfig/networking/profiles/default
cp -r etc $RPM_BUILD_ROOT

# RPM is smart. If we create these hard links in the install phase
# they become hard links when the RPM is installed - don't have
# to do it with a %post script
cd $RPM_BUILD_ROOT/etc/sysconfig
if [ ! network-scripts/ifcfg-iridium -ef networking/devices/ifcfg-iridium ]; then
    rm -f networking/devices/ifcfg-iridium
    ln network-scripts/ifcfg-iridium networking/devices
fi
if [ ! network-scripts/ifcfg-iridium -ef networking/profiles/default/ifcfg-iridium ]; then
    rm -f networking/profiles/default/ifcfg-iridium
    ln network-scripts/ifcfg-iridium networking/profiles/default
fi

%pre

# try to guess if a pap-secrets has a password for our RAS account
# without divulging entire account name or password
raspasswd=false
(egrep "^[\"]*raf" /etc/ppp/pap-secrets | egrep -q -v None) && raspasswd=true
if ! $raspasswd; then
    echo "/etc/ppp/pap-secrets file does not seem to contain an entry \
for our Level3 RAS account. This file must be edited by \
hand to add a password for the account."
fi

%post

# disable /etc/ppp/options.
if [ -f /etc/ppp/options ]; then
    osize=`wc -w /etc/ppp/options |  cut -f 1 -d \ `
    if [ $osize -gt 0 ]; then
        echo "/etc/ppp/options has non-zero size, and it may conflict with raf-satcom-iridium. Renaming the original to /etc/ppp/options.disable"
        mv /etc/ppp/options /etc/ppp/options.disable
    fi
fi
touch /etc/ppp/options



%clean
rm -rf $RPM_BUILD_ROOT

%files
# If a file does not change between RPM versions, then locally edited
# %config files are not altered (no overwriting and no .rpmnew or .rpmsave).
# If a file is changed from one package version to another then
# use %config if you want locally changed files to be renamed to .rpmsave,
# Use %config(noreplace) if you want locally changed
# files to be left alone, and newly installed files to become .rpmnew
%defattr(-,root,root)
%config /etc/sysconfig/network-scripts/ifcfg-iridium
%config /etc/sysconfig/networking/devices/ifcfg-iridium
%config /etc/sysconfig/networking/profiles/default/ifcfg-iridium
%config /etc/ppp/options.ttyS0
%config /etc/ppp/options.ttyACM0
%config /etc/ppp/options.ttyACM1
%config /etc/ppp/peers/iridium
%config /etc/ppp/peers/iridium.chat
%config /etc/ppp/peers/iridium-direct
%config /etc/ppp/peers/iridium-direct.chat
%config(noreplace) %attr(0600,root,root) /etc/ppp/pap-secrets

%changelog
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
