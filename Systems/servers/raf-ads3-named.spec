
# predefined
# %{_localstatedir} = /var

# Pieces of this were stolen from bind.spec of bind-9.5.0-16.a6.fc8.src.rpm
%define         do_chroot 0
%define         bind_dir      /var/named
%define         chroot_prefix %{bind_dir}/chroot

Summary: DNS/named configuration for RAF aircraft server
Name: raf-ads3-named
Version: 1.0
Release: 11
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# BuildRoot is only needed by older rpm versions
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Source: %{name}-%{version}.tar.gz

%description
DNS/named configuration for RAF aircraft server

# We're splitting this into two subpackages, raf-ac-named for the
# aircraft, and raf-lab-named for lab systems.
%package -n raf-ac-named
Summary: DNS/named configuration for RAF aircraft server
Group: System Environment/Daemons
Requires: bind
%if %{do_chroot}
Requires: bind-chroot
%endif
%description -n raf-ac-named
Summary: DNS/named configuration for RAF aircraft server.

%package -n raf-lab-named
Summary: DNS/named configuration for RAF lab system
Group: System Environment/Daemons
Requires: bind
%if %{do_chroot}
Requires: bind-chroot
%endif
%description -n raf-lab-named
DNS/named configuration for RAF lab system.

%prep
%setup -n %{name}

%build

%install
rm -fr $RPM_BUILD_ROOT

# install files to /var/named (bind_dir) and /etc
# Then in the triggerin script, optionally run
# /usr/sbin/bind-chroot-admin which moves the files to
# /var/named/chroot/var/named and creates links on /var/named
install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d ${RPM_BUILD_ROOT}%{bind_dir}
install -d $RPM_BUILD_ROOT/usr/local/admin

cp -r etc/* $RPM_BUILD_ROOT%{_sysconfdir}
cp -r var/named/* $RPM_BUILD_ROOT%{bind_dir}
cp -r usr/local/admin/raf-ads3-named $RPM_BUILD_ROOT/usr/local/admin

%triggerin -n raf-ac-named -- bind bind-chroot
export SYSCONFDIR=%{_sysconfdir}
export DO_CHROOT=%{do_chroot}
/usr/local/admin/raf-ads3-named/triggerin.sh ac %{name}-%{version}

%triggerin -n raf-lab-named -- bind bind-chroot
export SYSCONFDIR=%{_sysconfdir}
export DO_CHROOT=%{do_chroot}
/usr/local/admin/raf-ads3-named/triggerin.sh lab %{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%files -n raf-ac-named
%defattr(0640,root,named,0750)

# files are installed to /etc and /var/named
%if %{do_chroot}
# If %{do_chroot}, the triggerin script runs bind-chroot-admin,
# which moves files matching /etc/named.* and /var/named/*
# (along with /etc/named.ac.conf and /etc/raf.ucar.edu.key)
# to /var/named/chroot and creates links to them
# from /var/named and /etc.
# Hence the two directives for each file below:
%config(noreplace) %verify(not link) %{_sysconfdir}/named.ac.conf
%ghost  %config(noreplace) %{chroot_prefix}/etc/named.ac.conf
%defattr(0660,named,named,0770)
%config(noreplace) %verify(not link) /var/named/raf.ucar.edu
%ghost  %config(noreplace) %{chroot_prefix}/var/named/raf.ucar.edu
%config(noreplace) %verify(not link) /var/named/192.168.184
%ghost  %config(noreplace) %{chroot_prefix}/var/named/192.168.184
%config(noreplace) %verify(not link) /var/named/192.168.84
%ghost  %config(noreplace) %{chroot_prefix}/var/named/192.168.84
%else
%config(noreplace) %{_sysconfdir}/named.ac.conf
%defattr(0660,named,named,0770)
%config(noreplace) /var/named/raf.ucar.edu
%config(noreplace) /var/named/192.168.184
%config(noreplace) /var/named/192.168.84
%endif

%dir /usr/local/admin/raf-ads3-named
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-named/triggerin.sh
%config /usr/local/admin/raf-ads3-named/named.*

# On aircraft, eth2 is a DHCP client interface.  This dhclient 
# configuration prevents DHCP from screwing up /etc/resolv.conf
%config(noreplace) /etc/dhclient-eth2.conf

%files -n raf-lab-named
%defattr(0640,root,named,0750)

# files are installed to /etc and /var/named
%if %{do_chroot}
# If %{do_chroot}, the triggerin script runs bind-chroot-admin,
# which moves files matching /etc/named.* and /var/named/*
# (along with /etc/named.lab.conf and /etc/raf.ucar.edu.key)
# to /var/named/chroot and creates links to them
# from /var/named and /etc.
# Hence the two directives for each file below:
%config(noreplace) %verify(not link) %{_sysconfdir}/named.lab.conf
%ghost  %config(noreplace) %{chroot_prefix}/etc/named.lab.conf
%defattr(0660,named,named,0770)
%config(noreplace) %verify(not link) /var/named/raf.ucar.edu
%ghost  %config(noreplace) %{chroot_prefix}/var/named/raf.ucar.edu
%config(noreplace) %verify(not link) /var/named/192.168.184
%ghost  %config(noreplace) %{chroot_prefix}/var/named/192.168.184
%config(noreplace) %verify(not link) /var/named/192.168.84
%ghost  %config(noreplace) %{chroot_prefix}/var/named/192.168.84
%else
%config(noreplace) %{_sysconfdir}/named.lab.conf
%defattr(0660,named,named,0770)
%config /var/named/raf.ucar.edu
%config /var/named/192.168.184
%config /var/named/192.168.84
%endif

%dir /usr/local/admin/raf-ads3-named
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-named/triggerin.sh
%config /usr/local/admin/raf-ads3-named/named.*

%changelog
* Tue Jul 26 2010 Gordon Maclean <maclean@ucar.edu> 1.0-11
- fix backwards logic when checking for existence of /var/named/log
* Tue Jun  1 2010 Gordon Maclean <maclean@ucar.edu> 1.0-10
- cvi-dsm-2, cvi-pc-2
* Thu Mar 18 2010 Gordon Maclean <maclean@ucar.edu> 1.0-9
- egrep -E fails under Fedora 12 (-E is redundant). Use grep -E, or just egrep
* Sat Jan 23 2010 Gordon Maclean <maclean@ucar.edu> 1.0-8
- Changed etc/dhclient-eth2.conf: from append to supercede domain-name "raf.ucar.edu";,
- so eol.ucar.edu shouldn't be searched for non-qualified names after the server
- comes up as a dhcp client on the guest net.
* Tue Dec  8 2009 Gordon Maclean <maclean@ucar.edu> 1.0-7
- Removed Requires: raf-ac-dhcp
* Thu Nov 13 2009 Chris Webster <cjw@ucar.edu> 1.0-6
- Fixed improper comment character from 1.0-5
* Thu Oct 15 2009 Gordon Maclean <maclean@ucar.edu> 1.0-5
- Added hardcoded address for psi9116
* Wed Dec 3 2008 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Added /etc/dhclient-eth2.conf
* Wed Oct 29 2008 Gordon Maclean <maclean@ucar.edu>
- Moved Requires into sub-package portion.
* Fri Oct 24 2008 Gordon Maclean <maclean@ucar.edu>
- small tweaks: noreplace on some configs,
- comment out ROOTDIR in /etc/sysconfig/named if not do_chroot.
* Sun Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
