Summary: Master package for UCAR RAF satcom network configuration
Name: raf-satcom
Version: 1.0
Release: 3
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Requires: raf-satcom-iridium

# LIC: GPL
%description
Master package for UCAR RAF satcom network configuration

%prep
%setup -n %{name}

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT
cp -r etc $RPM_BUILD_ROOT

%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0755,root,root) /etc/ppp/ip-up.local
%attr(0755,root,root) /etc/ppp/ip-pre-up
%attr(0755,root,root) /etc/ppp/ip-pre-up.local

%changelog
* Mon Oct  6 2008 Gordon Maclean <maclean@ucar.edu>
- Added ip-pre-up scripts
* Tue Mar  4 2008 Gordon Maclean <maclean@ucar.edu>
- With "unit N" pppd option the device name will always be pppN

* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
