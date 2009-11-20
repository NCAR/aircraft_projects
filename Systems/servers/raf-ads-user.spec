Summary: 'ads' user files.
Name: raf-ads-user
Version: 1
Release: 1
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
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
cp -rp home $RPM_BUILD_ROOT

%files
%config(noreplace) %attr(-,ads,ads) /home/ads/.Jeffco_only.cshrc
%config(noreplace) %attr(-,ads,ads) /home/ads/.System.cshrc
%config(noreplace) %attr(-,ads,ads) /home/ads/.cshrc
%config(noreplace) %attr(-,ads,ads) /home/ads/.my_defaults

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Thu Nov 19 2009 John Wasinger <wasinger@ucar.edu> 1.0
- Initial release
