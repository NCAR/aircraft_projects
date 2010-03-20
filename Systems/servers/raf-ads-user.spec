Summary: 'ads' user files.
Name: raf-ads-user
Version: 1
Release: 12
Group: User/Environment
Source: %{name}-%{version}.tar.gz
License: none
# BuildRoot is only needed by older rpm versions
BuildRoot: %{_tmppath}/%{name}
BuildArch: noarch

%description
Provides the 'ads' user cshrc files.

%prep
%setup -n %{name}

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}/home/ads/bin

cp home/ads/System.cshrc             ${RPM_BUILD_ROOT}/home/ads/.System.cshrc
cp home/ads/Jeffco_only.cshrc        ${RPM_BUILD_ROOT}/home/ads/.Jeffco_only.cshrc
cp home/ads/cshrc                    ${RPM_BUILD_ROOT}/home/ads/.cshrc
cp home/ads/my_defaults              ${RPM_BUILD_ROOT}/home/ads/.my_defaults
cp home/ads/ads3_environment.csh     ${RPM_BUILD_ROOT}/home/ads/ads3_environment.csh
cp home/ads/login                    ${RPM_BUILD_ROOT}/home/ads/.login
cp home/ads/bin/svn-ask-username.sh  ${RPM_BUILD_ROOT}/home/ads/bin/svn-ask-username.sh
cp home/ads/bin/foldertab            ${RPM_BUILD_ROOT}/home/ads/bin/foldertab

%files
%defattr(-,ads,ads)
%config /home/ads/.Jeffco_only.cshrc
%config /home/ads/.System.cshrc
%config /home/ads/.cshrc
%config /home/ads/.my_defaults
%config /home/ads/ads3_environment.csh
%config /home/ads/.login
%config /home/ads/bin/svn-ask-username.sh
%config /home/ads/bin/foldertab

%post
chown -R ads:ads /home/ads/bin

echo
echo "  Make sure ads uid is 12900, and ads gid is 1318 !!"
echo
echo "  If your installing this on an aircraft then fix the AIRCRAFT"
echo "  variable in ~/ads3_environment.csh !!!"
echo

%clean
rm -rf ${RPM_BUILD_ROOT}

%changelog
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
