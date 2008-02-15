Summary: ddclient perl script and supporting scripts for running ddclient from pppd
Name: raf-ddclient
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
Patch0: ddclient-mail-on-kill.patch

# LIC: GPL
%description
ddclient perl script and supporting scripts for running ddclient from pppdon

%prep
%setup -n %{name}
cd usr/sbin
ls
%patch0
ls

%build

%install
install -d $RPM_BUILD_ROOT
cp -r etc $RPM_BUILD_ROOT
cp -r usr $RPM_BUILD_ROOT

%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0755,root,root) /usr/sbin/ddclient
%config /etc/ddclient/ddclient.conf
%attr(0755,root,root) /etc/ppp/run_ddclient.sh

%changelog
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
