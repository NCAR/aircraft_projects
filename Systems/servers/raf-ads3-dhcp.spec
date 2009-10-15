Summary: DHCP configuration for server on RAF aircraft
Name: raf-ads3-dhcp
Version: 1.0
Release: 11
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Source: %{name}-%{version}.tar.gz

%description
DHCP configuration for RAF aircraft server

%prep
%setup -n %{name}

# We're splitting this into two subpackages, for the GV and C130.
# Since a dhcp config can have multiple entries with different MAC
# addresses for the same ddns-hostname, perhaps we don't 
# really need separate packages, but ...
# Also need a lab package.
%package -n raf-gv-dhcp
Summary: DHCP configuration for server system on GV
Group: System Environment/Daemons
Requires: dhcp bind
# Specify that this package provides the virtual capability raf-ac-dhcp
# which is required by raf-ac-named.  Similarly for raf-c130-dhcp
Provides: raf-ac-dhcp
%description -n raf-gv-dhcp
DHCP configuration for server system on GV.

%package -n raf-c130-dhcp
Summary: DHCP configuration for server system on C130
Group: System Environment/Daemons
Requires: dhcp bind
Provides: raf-ac-dhcp
%description -n raf-c130-dhcp
DHCP configuration for server system on C130.

%package -n raf-lab-dhcp
Summary: DHCP configuration for ADS3 data server in lab 
Group: System Environment/Daemons
Requires: dhcp bind
%description -n raf-lab-dhcp
DHCP configuration for ADS3 data server in lab.

%build

%install
rm -fr $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT/usr/local/admin
cp -r etc/* $RPM_BUILD_ROOT%{_sysconfdir}
cp -r usr/local/admin/raf-ads3-dhcp $RPM_BUILD_ROOT/usr/local/admin

%triggerin -n raf-gv-dhcp -- dhcp
export SYSCONFDIR=%{_sysconfdir}
/usr/local/admin/raf-ads3-dhcp/triggerin.sh gv raf-gv-dhcp

%triggerin -n raf-c130-dhcp -- dhcp
export SYSCONFDIR=%{_sysconfdir}
/usr/local/admin/raf-ads3-dhcp/triggerin.sh c130 raf-c130-dhcp

%triggerin -n raf-lab-dhcp -- dhcp
export SYSCONFDIR=%{_sysconfdir}
/usr/local/admin/raf-ads3-dhcp/triggerin.sh lab raf-lab-dhcp

%clean
rm -rf $RPM_BUILD_ROOT

%files -n raf-gv-dhcp
%defattr(-,root,root)
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-NCAR-README.txt
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-ac.conf
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-gv.conf
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-dsms.conf
# %config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dhcpd-local.conf
%ghost %config %attr(0640,root,named) %verify(not link) %{_sysconfdir}/raf.ucar.edu.key
%dir /usr/local/admin/raf-ads3-dhcp
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-dhcp/triggerin.sh

%files -n raf-c130-dhcp
%defattr(-,root,root)
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-NCAR-README.txt
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-ac.conf
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-c130.conf
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-dsms.conf
# %config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dhcpd-local.conf
%ghost %config %attr(0640,root,named) %verify(not link) %{_sysconfdir}/raf.ucar.edu.key
%dir /usr/local/admin/raf-ads3-dhcp
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-dhcp/triggerin.sh

%files -n raf-lab-dhcp
%defattr(-,root,root)
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-NCAR-README.txt
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-lab.conf
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-dsms.conf
# %config(noreplace) %attr(0644,root,root) %{_sysconfdir}/dhcpd-local.conf
%ghost %config %attr(0640,root,named) %verify(not link) %{_sysconfdir}/raf.ucar.edu.key
%dir /usr/local/admin/raf-ads3-dhcp
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-dhcp/triggerin.sh

%changelog
* Thu Oct 15 2009 Gordon Maclean <maclean@ucar.edu> 1.0-11
- In triggerin.sh, add more checks for good keys.
* Tue Mar 24 2009 John Wasinger <wasinger@ucar.edu>
- Added vulcan-00658
* Fri Oct 30 2008 Gordon Maclean <maclean@ucar.edu>
- Added bind dependency so that the dndsec-keygen command is available
- for the trigger script.
* Fri Oct 24 2008 Gordon Maclean <maclean@ucar.edu>
- Fixed up generation of key
* Tue Apr 22 2008 Gordon Maclean <maclean@ucar.edu>
- Changed DSMs to fixed-addresses: 100-159
* Thu Mar  6 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
