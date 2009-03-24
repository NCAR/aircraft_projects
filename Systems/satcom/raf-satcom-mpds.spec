Summary: PPP and PPPOE configuration for Inmarsat MPDS
Name: raf-satcom-mpds
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
BuildArch: noarch

# LIC: GPL
%description
/etc files for configuring pppoe and ppp for Inmarsat MPDS

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
for f in ifcfg-mpds ifcfg-eth3; do
    for d in networking/devices networking/profiles/default; do
        if [ ! network-scripts/$f -ef $d/$f ]; then
            rm -f $d/$f
            ln network-scripts/$f $d
        fi
    done
done

%triggerin -- ppp

# disable /etc/ppp/options.  I think the default version from the ppp RPM
# contains a "lock" option, which I believe will fail on an ethernet port
# (need to check). In any case it may contain options which we don't want.
# pppd still requires it though, so we create an empty one.
if [ -f /etc/ppp/options ]; then
    osize=`wc -w /etc/ppp/options |  cut -f 1 -d \ `
    if [ $osize -gt 0 ]; then
        echo "/etc/ppp/options has non-zero size, and it may conflict with raf-satcom-mpds. Renaming the original to /etc/ppp/options.disable"
        mv /etc/ppp/options /etc/ppp/options.disable
    fi
fi
touch /etc/ppp/options

muser=`egrep  "^[:space:]*USER=" /etc/sysconfig/network-scripts/ifcfg-mpds | sed "s/.*=[\"']*\([^\"']*\)[\"']*/\1/"`

if [ -n $muser ]; then
    if ! egrep "^[:space:]*[^#]" /etc/ppp/pap-secrets | fgrep -q $muser; then
        echo "###### from %{name}-%{version} ######
${muser} 	mpds 	None
###### end %{name}-%{version} ######" >> /etc/ppp/pap-secrets
    fi
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
%config /etc/sysconfig/network-scripts/ifcfg-mpds
%config /etc/sysconfig/networking/devices/ifcfg-mpds
%config /etc/sysconfig/networking/profiles/default/ifcfg-mpds
%config /etc/sysconfig/network-scripts/ifcfg-eth3
%config /etc/sysconfig/networking/devices/ifcfg-eth3
%config /etc/sysconfig/networking/profiles/default/ifcfg-eth3
%config /etc/ppp/ip-up.mpds
%config /etc/ppp/options.eth3
%config /etc/ppp/pppoe-lost

%changelog
* Fri Jan 6 2009 Gordon Maclean <maclean@ucar.edu> 1.0-5
- changed post script to a trigger script so that we can patchup pap-secrets
- if ppp package messes with it.
* Fri Apr 11 2008 Gordon Maclean <maclean@ucar.edu> 1.0-4
- removed passive option for mpds, LCP_INTERVALfrom 40 to 20,
- and LCP_FAILURE from 6 to 3
* Sun Mar 10 2008 Gordon Maclean <maclean@ucar.edu>
- added ifcfg-eth3 config
* Sun Mar  9 2008 Gordon Maclean <maclean@ucar.edu>
- added pppoe-lost script, turn off persist
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
