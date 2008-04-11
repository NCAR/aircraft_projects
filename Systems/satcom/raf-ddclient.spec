Summary: ddclient perl script and supporting scripts for running ddclient from pppd
Name: raf-ddclient
Version: 1.0
Release: 2
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
ddclient perl script and supporting scripts for running ddclient from pppd

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
%dir /etc/ddclient
%config %attr(0640,root,root) /etc/ddclient/ddclient.conf
%attr(0755,root,root) /etc/ppp/run_ddclient.sh

%changelog
* Fri Apr 11 2008 Gordon Maclean <maclean@ucar.edu>
- run_ddclient.sh: add acserver as allowed hostname
- We need to be able to differentiate between gv and c130.
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
