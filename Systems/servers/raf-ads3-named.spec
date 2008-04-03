
# predefined
# %{_localstatedir} = /var

# Pieces of this were stolen from bind.spec of bind-9.5.0-16.a6.fc8.src.rpm
%define         do_chroot 0
%define         bind_dir      /var/named
%define         chroot_prefix %{bind_dir}/chroot

Summary: DNS/named configuration for RAF aircraft server
Name: raf-ads3-named
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch

Requires: bind raf-ads3-dhcp
# %if %(%{expand:test %{do_chroot} -ne 0; echo $?})
# Requires: bind-chroot
# %endif

# %{?do_chroot:Requires: bind-chroot}

%if %{do_chroot}
Requires: bind-chroot
%endif

Source: %{name}-%{version}.tar.gz

%description
DNS/named configuration for RAF aircraft server

# We're splitting this into two subpackages, raf-ac-named for the
# aircraft, and raf-lab-named for lab systems.
%package -n raf-ac-named
Summary: DNS/named configuration for RAF aircraft server
Group: System Environment/Daemons
%description -n raf-ac-named
Summary: DNS/named configuration for RAF aircraft server.

%package -n raf-lab-named
Summary: DNS/named configuration for RAF lab system
Group: System Environment/Daemons
%description -n raf-lab-named
DNS/named configuration for RAF lab system.

%prep
%setup -n %{name}

%build

%install

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

%triggerin -n raf-ac-named -- bind
export SYSCONFDIR=%{_sysconfdir}
export DO_CHROOT=%{do_chroot}
/usr/local/admin/raf-ads3-named/triggerin.sh ac %{name}-%{version}

%triggerin -n raf-lab-named -- bind
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
%config %verify(not link) %{_sysconfdir}/named.ac.conf
%ghost  %config %{chroot_prefix}/etc/named.ac.conf
%config %verify(not link) /var/named/raf.ucar.edu
%ghost  %config %{chroot_prefix}/var/named/raf.ucar.edu
%config %verify(not link) /var/named/192.168.184
%ghost  %config %{chroot_prefix}/var/named/192.168.184
%config %verify(not link) /var/named/192.168.84
%ghost  %config %{chroot_prefix}/var/named/192.168.84
%else
%config %{_sysconfdir}/named.ac.conf
%config /var/named/raf.ucar.edu
%config /var/named/192.168.184
%config /var/named/192.168.84
%endif

%dir /usr/local/admin/raf-ads3-named
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-named/triggerin.sh
%config /usr/local/admin/raf-ads3-named/named.*

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
%config %verify(not link) %{_sysconfdir}/named.lab.conf
%ghost  %config %{chroot_prefix}/etc/named.lab.conf
%config %verify(not link) /var/named/raf.ucar.edu
%ghost  %config %{chroot_prefix}/var/named/raf.ucar.edu
%config %verify(not link) /var/named/192.168.184
%ghost  %config %{chroot_prefix}/var/named/192.168.184
%config %verify(not link) /var/named/192.168.84
%ghost  %config %{chroot_prefix}/var/named/192.168.84
%else
%config %{_sysconfdir}/named.lab.conf
%config /var/named/raf.ucar.edu
%config /var/named/192.168.184
%config /var/named/192.168.84
%endif

%dir /usr/local/admin/raf-ads3-named
%config %attr(0755,root,root) /usr/local/admin/raf-ads3-named/triggerin.sh
%config /usr/local/admin/raf-ads3-named/named.*

%changelog
* Sun Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version

