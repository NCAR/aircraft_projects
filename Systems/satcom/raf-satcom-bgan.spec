Summary: PPP and PPPOE configuration for Inmarsat BGAN
Name: raf-satcom-bgan
Version: 1.0
Release: 5
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
Requires: rp-pppoe >= 3.8-2
Requires: ppp >= 2.4.4
# User must remove raf-satcom-mpds if it exists, because it contains
# contains some of the same files as this package, like /etc/ppp/options.eth3.
# Removing raf-satcom-mpds in the %pre stage is too late.
Conflicts: raf-satcom-mpds
Obsoletes: raf-satcom-bgan
BuildArch: noarch

# LIC: GPL
%description
/etc files for configuring pppoe and ppp for Inmarsat BGAN

%package -n raf-gv-satcom-bgan
Summary: bgan satcom client for server systems on GV
Group: System Environment/Daemons
%description -n raf-gv-satcom-bgan
bgan satcom for server system on GV.

%package -n raf-c130-satcom-bgan
Summary: bgan satcom client for server systems on C130
Group: System Environment/Daemons
%description -n raf-c130-satcom-bgan
bgan satcom for server system on C130.

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
# Link these files into these other directories
for f in ifcfg-bgan ifcfg-eth3; do
    for d in networking/devices networking/profiles/default; do
        if [ ! network-scripts/$f -ef $d/$f ]; then
            rm -f $d/$f
            ln network-scripts/$f $d
        fi
    done
done

%post -n raf-gv-satcom-bgan

# disable /etc/ppp/options.  I think the default version from the ppp RPM
# contains a "lock" option, which I believe will fail on an ethernet port
# (need to check). In any case it may contain options which we don't want.
# pppd still requires it though, so we create an empty one.
if [ -f /etc/ppp/options ]; then
    osize=`wc -w /etc/ppp/options |  cut -f 1 -d \ `
    if [ $osize -gt 0 ]; then
        echo "/etc/ppp/options has non-zero size, and it may conflict with raf-satcom-bgan. Renaming the original to /etc/ppp/options.disable"
        mv /etc/ppp/options /etc/ppp/options.disable
    fi
fi
touch /etc/ppp/options

muser=`grep  "^[[:space:]]*USER=" /etc/sysconfig/network-scripts/ifcfg-bgan | sed "s/.*=[\"']*\([^\"']*\)[\"']*/\1/"`

if [ -n $muser ]; then
    if ! grep "^[[:space:]]*[^#]" /etc/ppp/pap-secrets | grep -q $muser; then
        echo "###### from %{name}-%{version} ######
${muser} 	bgan 	None
###### end %{name}-%{version} ######" >> /etc/ppp/pap-secrets
    fi
fi
chmod 600 /etc/ppp/pap-secrets

sed -i 's,^SERVICENAME=.*,#SERVICENAME=PacketData,' /etc/sysconfig/network-scripts/ifcfg-bgan

%post -n raf-c130-satcom-bgan

# disable /etc/ppp/options.  I think the default version from the ppp RPM
# contains a "lock" option, which I believe will fail on an ethernet port
# (need to check). In any case it may contain options which we don't want.
# pppd still requires it though, so we create an empty one.
if [ -f /etc/ppp/options ]; then
    osize=`wc -w /etc/ppp/options |  cut -f 1 -d \ `
    if [ $osize -gt 0 ]; then
        echo "/etc/ppp/options has non-zero size, and it may conflict with raf-satcom-bgan. Renaming the original to /etc/ppp/options.disable"
        mv /etc/ppp/options /etc/ppp/options.disable
    fi
fi
touch /etc/ppp/options

muser=`grep  "^[[:space:]]*USER=" /etc/sysconfig/network-scripts/ifcfg-bgan | sed "s/.*=[\"']*\([^\"']*\)[\"']*/\1/"`

if [ -n $muser ]; then
    if ! grep "^[[:space:]]*[^#]" /etc/ppp/pap-secrets | grep -q $muser; then
        echo "###### from %{name}-%{version} ######
${muser} 	bgan 	None
###### end %{name}-%{version} ######" >> /etc/ppp/pap-secrets
    fi
fi
chmod 600 /etc/ppp/pap-secrets

sed -i 's,^SERVICENAME=.*,SERVICENAME=PacketData,' /etc/sysconfig/network-scripts/ifcfg-bgan


%clean
rm -rf $RPM_BUILD_ROOT

%files -n raf-gv-satcom-bgan
# If a file does not change between RPM versions, then locally edited
# %config files are not altered (no overwriting and no .rpmnew or .rpmsave).
# If a file is changed from one package version to another then
# use %config if you want locally changed files to be renamed to .rpmsave,
# Use %config(noreplace) if you want locally changed
# files to be left alone, and newly installed files to become .rpmnew
%defattr(-,root,root)
%config /etc/sysconfig/network-scripts/ifcfg-bgan
%config /etc/sysconfig/network-scripts/ifup-pre-bgan
%config /etc/sysconfig/networking/devices/ifcfg-bgan
%config /etc/sysconfig/networking/profiles/default/ifcfg-bgan
%config /etc/sysconfig/network-scripts/ifcfg-eth3
%config /etc/sysconfig/networking/devices/ifcfg-eth3
%config /etc/sysconfig/networking/profiles/default/ifcfg-eth3
%config /etc/logrotate.d/pppd_bgan
%attr(0755,root,root) /etc/ppp/ip-up.bgan
%attr(0755,root,root) /etc/ppp/ip-pre-up.bgan
%attr(0755,root,root) /etc/ppp/ip-down.bgan
%config /etc/ppp/options.eth3
%attr(0755,root,root) /etc/ppp/pppoe-lost

%files -n raf-c130-satcom-bgan
# If a file does not change between RPM versions, then locally edited
# %config files are not altered (no overwriting and no .rpmnew or .rpmsave).
# If a file is changed from one package version to another then
# use %config if you want locally changed files to be renamed to .rpmsave,
# Use %config(noreplace) if you want locally changed
# files to be left alone, and newly installed files to become .rpmnew
%defattr(-,root,root)
%config /etc/sysconfig/network-scripts/ifcfg-bgan
%config /etc/sysconfig/network-scripts/ifup-pre-bgan
%config /etc/sysconfig/networking/devices/ifcfg-bgan
%config /etc/sysconfig/networking/profiles/default/ifcfg-bgan
%config /etc/sysconfig/network-scripts/ifcfg-eth3
%config /etc/sysconfig/networking/devices/ifcfg-eth3
%config /etc/sysconfig/networking/profiles/default/ifcfg-eth3
%config /etc/logrotate.d/pppd_bgan
%attr(0755,root,root) /etc/ppp/ip-up.bgan
%attr(0755,root,root) /etc/ppp/ip-pre-up.bgan
%attr(0755,root,root) /etc/ppp/ip-down.bgan
%config /etc/ppp/options.eth3
%attr(0755,root,root) /etc/ppp/pppoe-lost

%changelog
* Tue Sep 30 2014 Tom Baltzer <tbaltzer@ucar.edu> 1.0-5
- Separate gv and c130 configs, need different SERVICENAMEs
* Thu May  3 2012 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Updated /etc/ppp/ip-up.bgan to turn off multicast, "ip link set $1 multicast off",
- after ppp is up.
* Mon Sep 26 2011 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added /etc/sysconfig/network-scripts/ifup-pre-bgan
* Tue Mar 2 2010 Gordon Maclean <maclean@ucar.edu> 1.0-2
- removed Obsoletes: raf-satcom-mpds. If B obsoletes A, and A is installed,
- yum will see a dependency there and yum update will install B. So yum update
- was trying to install this raf-satcom-bgan on the GV - not what I wanted.
- Instead we'll do an rpm -e raf-satcom-mpds in the %pre - see if that works.
* Fri Nov 6 2009 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial version
