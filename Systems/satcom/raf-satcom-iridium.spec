Summary: Configuration for PPP over Iridium
Name: raf-satcom-iridium
Version: 1.0
Release: 6
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
Requires: ppp >= 2.4.4
BuildArch: noarch

# LIC: GPL
%description
/etc files for configuring pppd over an Iridium connection

%prep
%setup -n %{name}

%build

%install
rm -rf $RPM_BUILD_ROOT
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

%triggerin -- ppp

# disable /etc/ppp/options.
if [ -f /etc/ppp/options ]; then
    osize=`wc -w /etc/ppp/options |  cut -f 1 -d \ `
    if [ $osize -gt 0 ]; then
        echo "/etc/ppp/options has non-zero size, and it may conflict with raf-satcom-iridium. Renaming the original to /etc/ppp/options.disable"
        mv /etc/ppp/options /etc/ppp/options.disable
    fi
fi
touch /etc/ppp/options

# Report if it looks like pap-secrets is missing an entry for the RAS
# account.
ent="`egrep '^[[:space:]]*[^#]' /etc/ppp/pap-secrets | egrep '^["]*raf'`"
if [ -z "$ent" ]; then
    echo "###### from %{name}-%{version} ######
raf 	iridium 	None-Yet
###### end %{name}-%{version} ######" >> /etc/ppp/pap-secrets
fi

if [ -z "$ent" ] || echo "$ent" | fgrep -iq none; then
    echo "Warning: /etc/ppp/pap-secrets file does not seem to contain an entry \
for our Level3 RAS account. This file must be edited by \
hand to add a password for the account."
fi
chmod 600 /etc/ppp/pap-secrets

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
%config /etc/ppp/options.ttyUSB0

%attr(0755,root,root) /etc/ppp/ip-up.iridium
%attr(0755,root,root) /etc/ppp/ip-pre-up.iridium
%config /etc/ppp/peers/iridium
%attr(0755,root,root) /etc/ppp/peers/iridium.chat
%config /etc/ppp/peers/iridium-direct
%attr(0755,root,root) /etc/ppp/peers/iridium-direct.chat
%attr(0755,root,root) /etc/ppp/peers/iridiumDC.chat

%changelog
* Fri Nov 20 2015 Tom Baltzer <tbaltzer@ucar.edu> 1.0-6
- Updates to work for ICEBRIDGE2015 and for use of NASA provided SIM card (commented out)
* Tue Oct 11 2011 Tom Baltzer <tbaltzer@ucar.edu> 1.0-5
- made mods to allow connectivity with NASA modem bank and ppp
- as well as new interface (ttyUSB0)
* Fri Jan 6 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- changed post script to a trigger script so that we can patchup pap-secrets
- if ppp package messes with it.
* Fri Sep 26 2008 Gordon Maclean <maclean@ucar.edu>
- added ip-up.iridium which runs ddclient
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
