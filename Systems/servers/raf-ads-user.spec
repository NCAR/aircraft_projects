Summary: 'ads' user files.
Name: raf-ads-user
Version: 1
Release: 6
Group: User/Environment
Source: %{name}-%{version}.tar.gz
License: none
Buildroot: %{_tmppath}/%{name}
BuildArch: noarch

%description
Provides the 'ads' user cshrc files.

%prep
%setup -n %{name}

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}/home/ads/bin

cp home/ads/System.cshrc ${RPM_BUILD_ROOT}/home/ads/.System.cshrc
cp home/ads/Jeffco_only.cshrc ${RPM_BUILD_ROOT}/home/ads/.Jeffco_only.cshrc
cp home/ads/cshrc ${RPM_BUILD_ROOT}/home/ads/.cshrc
cp home/ads/my_defaults ${RPM_BUILD_ROOT}/home/ads/.my_defaults
cp home/ads/ads3_environment.csh ${RPM_BUILD_ROOT}/home/ads/ads3_environment.csh
cp home/ads/login ${RPM_BUILD_ROOT}/home/ads/.login
cp home/ads/bin/svn-ask-username.sh ${RPM_BUILD_ROOT}/home/ads/bin/svn-ask-username.sh

%files
%defattr(-,ads,ads)
%config /home/ads/.Jeffco_only.cshrc
%config /home/ads/.System.cshrc
%config /home/ads/.cshrc
%config /home/ads/.my_defaults
%config /home/ads/ads3_environment.csh
%config /home/ads/.login
%config /home/ads/bin/svn-ask-username.sh

%post
chown -R ads:ads /home/ads/bin

echo "\n   Make sure ads uid is 12900, and ads gid is 1381!\n"

%clean
rm -rf ${RPM_BUILD_ROOT}

%changelog
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
