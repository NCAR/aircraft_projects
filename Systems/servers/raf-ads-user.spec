Summary: 'ads' user files.
Name: raf-ads-user
Version: 1
Release: 19
Group: User/Environment
Source: %{name}-%{version}.tar.gz
License: none
# BuildRoot is only needed by older rpm versions
BuildRoot: %{_tmppath}/%{name}
BuildArch: noarch

Requires: xchat
Requires: firefox

%description
Provides the 'ads' user cshrc files.

%prep
%setup -n %{name}

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}/home/ads/bin
mkdir -p ${RPM_BUILD_ROOT}/home/ads/Desktop

cp home/ads/System.cshrc             ${RPM_BUILD_ROOT}/home/ads/.System.cshrc
cp home/ads/Jeffco_only.cshrc        ${RPM_BUILD_ROOT}/home/ads/.Jeffco_only.cshrc
cp home/ads/cshrc                    ${RPM_BUILD_ROOT}/home/ads/.cshrc
cp home/ads/my_defaults              ${RPM_BUILD_ROOT}/home/ads/.my_defaults
cp home/ads/ads3_environment.csh     ${RPM_BUILD_ROOT}/home/ads/ads3_environment.csh
cp home/ads/login                    ${RPM_BUILD_ROOT}/home/ads/.login
cp home/ads/bin/*                    ${RPM_BUILD_ROOT}/home/ads/bin
cp home/ads/Desktop/*                ${RPM_BUILD_ROOT}/home/ads/Desktop
cp -r home/ads/.ssh                  ${RPM_BUILD_ROOT}/home/ads

%trigger -- nidas-daq
# set contents of /var/lib/nidas/DaqUser to "ads", and set ownership of /var/run/nidas
if [ ! grep -q ads %{_sharedstatedir}/nidas/DaqUser ]; then
    echo "ads" > %{_sharedstatedir}/nidas/DaqUser
fi
chown -R ads %{_localstatedir}/run/nidas
group=`id -gn ads`
if [ -n "$group" ]; then
    chgrp -R $group %{_localstatedir}/run/nidas
fi

%files
%defattr(-,ads,ads)
%config /home/ads/.Jeffco_only.cshrc
%config /home/ads/.System.cshrc
%config /home/ads/.cshrc
%config /home/ads/.my_defaults
%config /home/ads/ads3_environment.csh
%config /home/ads/.login
%config %attr(0600,ads,ads) /home/ads/.ssh/config
%attr(0775,ads,ads) /home/ads/bin/swcreate
%attr(0775,ads,ads) /home/ads/bin/svn-ask-username.sh
%attr(0755,ads,ads) /home/ads/bin/foldertab
%attr(0755,ads,ads) /home/ads/Desktop/AutoCal.desktop
%attr(0755,ads,ads) /home/ads/Desktop/CalibrationDatabaseEditor.desktop
%attr(0755,ads,ads) /home/ads/Desktop/ConfigEditor.desktop
%attr(0755,ads,ads) /home/ads/Desktop/aeros.desktop
%attr(0755,ads,ads) /home/ads/Desktop/nimbus.desktop
%attr(0755,ads,ads) /home/ads/Desktop/start_data_acq.desktop
%attr(0755,ads,ads) /home/ads/Desktop/start_mpds.desktop
%attr(0755,ads,ads) /home/ads/Desktop/start_iridium.desktop
%attr(0755,ads,ads) /home/ads/Desktop/stop_data_acq.desktop
%attr(0755,ads,ads) /home/ads/Desktop/stop_mpds.desktop
%attr(0755,ads,ads) /home/ads/Desktop/stop_iridium.desktop

%pre
# Add an ads user and ads and eol groups to system

adduser=false
addeolgroup=false
addadsgroup=false
grep -q ^ads /etc/passwd || adduser=true
grep -q ^eol /etc/group || addeolgroup=true
grep -q ^ads /etc/group || addadsgroup=true

# check if NIS is running. If so, check if user and group are known to NIS
if which ypwhich > /dev/null 2>&1 && ypwhich > /dev/null 2>&1; then
    ypmatch ads passwd > /dev/null 2>&1 && adduser=false
    ypmatch eol group > /dev/null 2>&1 && addeolgroup=false
    ypmatch ads group > /dev/null 2>&1 && addadsgroup=false
fi

$addeolgroup && /usr/sbin/groupadd -g 1342 -o eol
$addadsgroup && /usr/sbin/groupadd -g 1318 -o ads
$adduser && /usr/sbin/useradd  -u 12900 -N -g ads -G eol -s /bin/csh -c "ADS operator" -K PASS_MAX_DAYS=-1 ads || :

if ! grep eol /etc/group | grep -q ads; then
    ypmatch eol group > /dev/null 2>&1 || usermod -G eol ads
fi

%post
chown -R ads:ads /home/ads/bin

echo
echo "  Make sure ads uid is 12900, and ads gid is 1318 !!"
echo
echo "  If your installing this on an aircraft then fix the AIRCRAFT and PROJECT"
echo "  variables in ~/ads3_environment.csh !!!"
echo

cf=/home/ads/.ssh/id_dsa_dsm
if ! [ -f /home/ads/.ssh/id_dsa_dsm ]; then
    echo "$cf private ssh key not found. Copy it from another system, and chmod 0600"
fi

%clean
rm -rf ${RPM_BUILD_ROOT}

%changelog
* Fri Jul 19 2013 John Wasinger <wasinger@ucar.edu> 1.19
- Added Auto Cal icon to desktop.
- Added Calibration Database Editor icon to desktop.
* Fri Apr 05 2013 Gordon Maclean <maclean@ucar.edu> 1.18
- Added .ssh/config
* Tue Apr 10 2012 Gordon Maclean <maclean@ucar.edu> 1.17
- Update nidas path to /opt/nidas/bin.
- Added trigger script to update ownership of /var/run/nidas and
- /var/lib/nidas/DaqUser when nidas-daq is updated.
* Thu Jan 12 2012 Tom Baltzer <tbaltzer@ucar.edu> 1.15
- Iridium icon added, clean up some elements
* Fri Aug 5 2011 Chris Webster <cjw@ucar.edu> 1.15
- Add Desktop and some icons.
* Mon May 16 2011 Gordon Maclean <maclean@ucar.edu> 1.15
- In %pre step add ads user and ads,eol groups if necessary.
- nidas-bin package installs files writeable by eol group, so we'll want
- ads to belong to eol group.
* Thu Jul 30 2010 Chris Webster <cjw@ucar.edu> 1.13
- add env COIN_FULL_INDIRECT_RENDERING to avoid aeros track plot crash.
* Thu Feb 18 2010 Chris Webster <cjw@ucar.edu> 1.12
- Remove setl binary.  tcsh has options in prompt command to update title.
* Thu Jan 21 2010 Chris Webster <cjw@ucar.edu> 1.11
- PATH updates.
* Wed Jan 13 2010 Chris Webster <cjw@ucar.edu> 1.10
- Correct env var name, from XMIT to XMIT_DIR
* Thu Dec 17 2009 John Wasinger <wasinger@ucar.edu> 1.9
- (re) added /home/ads/bin/setl file.
* Wed Dec 16 2009 John Wasinger <wasinger@ucar.edu> 1.8
- Spaced out 'install' cp list for clearity.
- Fixed prompt to use hostname when not installed on an aircraft.
- Removed '\n' strings in echo statement.  Did not create desired effect.
- Added /home/ads/bin/foldertab
* Fri Dec 11 2009 Chris Webster <cjw@ucar.edu> 1.7
- Remove prompt stuff from System.cshrc
- Remove $MYOS.  Should use $OSTYPE anyways.
- Moved source'ing of ads3_environment.csh from .login to .my_defaults.
- Added setl binary (I don't know where the source is anymore).
* Fri Dec 04 2009 Chris Webster <cjw@ucar.edu> 1.6
- Add PGGRND variable for ground database.
- Prompt clean up.
* Fri Dec 04 2009 John Wasinger <wasinger@ucar.edu> 1.5
- chown -R ads:ads /home/ads/bin
* Mon Nov 30 2009 John Wasinger <wasinger@ucar.edu> 1.4
- Now creates '.rpmsave' files to back up previous changes.
- Fixed prompt string.
* Thu Nov 23 2009 John Wasinger <wasinger@ucar.edu> 1.3
- Added bin/svn-ask-username.sh
* Thu Nov 23 2009 John Wasinger <wasinger@ucar.edu> 1.2
- Added .login and ads3_environment.csh, clean up .my_defaults
* Thu Nov 19 2009 John Wasinger <wasinger@ucar.edu> 1.1
- Initial release
