Summary: ddclient perl script and supporting scripts for running ddclient from pppd
Name: raf-ddclient
Version: 1.0
Release: 5
License: GPL
Group: System Environment/Daemons
Source: %{name}-%{version}.tar.gz
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
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
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT
cp -r etc $RPM_BUILD_ROOT
cp -r usr $RPM_BUILD_ROOT

%post -n raf-gv-ddclient
sed -i 's,^SYSNAME=.*,SYSNAME=gv,' /etc/ppp/run_ddclient.sh

%post -n raf-c130-ddclient
sed -i 's,^SYSNAME=.*,SYSNAME=c130,' /etc/ppp/run_ddclient.sh

%clean
rm -rf $RPM_BUILD_ROOT

# If a file does not change between RPM versions, then locally edited
# %config files are not altered (no overwriting and no .rpmnew or .rpmsave).
# If a file is changed from one package version to another then
# use %config if you want locally changed files to be renamed to .rpmsave,
# Use %config(noreplace) if you want locally changed
# files to be left alone, and newly installed files to become .rpmnew
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
* Sat Jan 23 2010 Gordon Maclean <maclean@ucar.edu> 1.0-5
- New version of run_ddclient.sh which uses checkip.dyndns.org to get IP.
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu>
- Bug fix in run_ddclient script
* Tue Apr 15 2008 Gordon Maclean <maclean@ucar.edu>
- Separate gv and c130 configs. Can't pass -host in runstring.
* Fri Apr 11 2008 Gordon Maclean <maclean@ucar.edu>
- run_ddclient.sh: add acserver as allowed hostname
- We need to be able to differentiate between gv and c130.
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
