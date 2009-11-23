Summary: 'ads' user files.
Name: raf-ads-user
Version: 1
Release: 2
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
mkdir -p ${RPM_BUILD_ROOT}/home/ads

cp home/ads/System.cshrc ${RPM_BUILD_ROOT}/home/ads/.System.cshrc
cp home/ads/Jeffco_only.cshrc ${RPM_BUILD_ROOT}/home/ads/.Jeffco_only.cshrc
cp home/ads/cshrc ${RPM_BUILD_ROOT}/home/ads/.cshrc
cp home/ads/my_defaults ${RPM_BUILD_ROOT}/home/ads/.my_defaults
cp home/ads/ads3_environment.csh ${RPM_BUILD_ROOT}/home/ads/ads3_environment.csh
cp home/ads/login ${RPM_BUILD_ROOT}/home/ads/.login

%files
%config(noreplace) %attr(-,ads,ads) /home/ads/.Jeffco_only.cshrc
%config(noreplace) %attr(-,ads,ads) /home/ads/.System.cshrc
%config(noreplace) %attr(-,ads,ads) /home/ads/.cshrc
%config(noreplace) %attr(-,ads,ads) /home/ads/.my_defaults
%config(noreplace) %attr(-,ads,ads) /home/ads/ads3_environment.csh
%config(noreplace) %attr(-,ads,ads) /home/ads/.login

%clean
rm -rf ${RPM_BUILD_ROOT}

%changelog
* Thu Nov 23 2009 John Wasinger <wasinger@ucar.edu> 1.2
- Added .login and ads3_environment.csh, clean up .my_defaults
* Thu Nov 19 2009 John Wasinger <wasinger@ucar.edu> 1.1
- Initial release
