Summary: Master package for UCAR RAF satcom network configuration
Name: raf-satcom
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch
Requires: raf-satcom-mpds
Requires: raf-satcom-iridium
Requires: raf-ddclient

# LIC: GPL
%description
Master package for UCAR RAF satcom network configuration

%prep
%setup -n %{name}

%build

%install
install -d $RPM_BUILD_ROOT
cp -r etc $RPM_BUILD_ROOT

%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0755,root,root) /etc/ppp/ip-up.local
%attr(0755,root,root) /etc/ppp/ip-pre-up

%changelog
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
