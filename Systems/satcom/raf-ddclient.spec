Summary: ddclient perl script and supporting scripts for running ddclient from pppd
Name: raf-ddclient
Version: 1.0
Release: 4
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch
Patch0: ddclient-mail-on-kill.patch
Obsoletes: raf-ddclient

# LIC: GPL
%description
ddclient perl script and supporting scripts for running ddclient from pppd

%prep
%setup -n %{name}
cd usr/sbin
ls
%patch0
ls

%package -n raf-gv-ddclient
Summary: ddclient for server system on GV
Group: System Environment/Daemons
%description -n raf-gv-ddclient
ddclient for server system on GV.

%package -n raf-c130-ddclient
Summary: ddclient for server system on C130
Group: System Environment/Daemons
%description -n raf-c130-ddclient
ddclient for server system on C130.

%build

%install
install -d $RPM_BUILD_ROOT
cp -r etc $RPM_BUILD_ROOT
cp -r usr $RPM_BUILD_ROOT

%post -n raf-gv-ddclient
sed -i 's,^SYSNAME=.*,SYSNAME=gv,' /etc/ppp/run_ddclient.sh

%post -n raf-c130-ddclient
sed -i 's,^SYSNAME=.*,SYSNAME=c130,' /etc/ppp/run_ddclient.sh
%

%clean
rm -rf $RPM_BUILD_ROOT

%files -n raf-gv-ddclient
%defattr(-,root,root)
%attr(0755,root,root) /usr/sbin/ddclient
%dir /etc/ddclient
%config %attr(0600,root,root) /etc/ddclient/gv.conf
%attr(0755,root,root) /etc/ppp/run_ddclient.sh

%files -n raf-c130-ddclient
%defattr(-,root,root)
%attr(0755,root,root) /usr/sbin/ddclient
%dir /etc/ddclient
%config %attr(0600,root,root) /etc/ddclient/c130.conf
%attr(0755,root,root) /etc/ppp/run_ddclient.sh

%changelog
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu>
- Bug fix in run_ddclient script
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu>
- Separate gv and c130 configs. Can't pass -host in runstring.
* Fri Apr 11 2008 Gordon Maclean <maclean@ucar.edu>
- run_ddclient.sh: add acserver as allowed hostname
- We need to be able to differentiate between gv and c130.
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
