
# predefined
# %{_localstatedir} = /var

# Pieces of this were stolen from bind.spec of bind-9.5.0-16.a6.fc8.src.rpm
%define         do_chroot 0
%define         bind_dir      /var/named
%define         chroot_prefix %{bind_dir}/chroot

Summary: DNS/named configuration for RAF aircraft server
Name: raf-ac-named
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch

Requires: bind raf-ac-dhcp
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

%prep
%setup -n %{name}

%build

%install


# install files to /var/named (bind_dir) and /etc
# Then in the triggerin script, run /usr/sbin/bind-chroot-admin
# which moves the files to /var/named/chroot/var/named and
# creates links on /var/named
install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d ${RPM_BUILD_ROOT}%{bind_dir}

cp -r etc/* $RPM_BUILD_ROOT%{_sysconfdir}
cp -r var/named/* $RPM_BUILD_ROOT%{bind_dir}
# localstatedir=/var.

%triggerin -- bind
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# The named package owns /etc/named.conf, so we must edit it
# in the triggerin script.

# Append an include of named.raf.conf if needed.
cf=%{_sysconfdir}/named.conf
if ! egrep -q '^[[:space:]]*include[[:space:]]+"%{_sysconfdir}/named.raf.conf"' $cf; then
    # use rpm -V to see if named.conf has been modified from the RPM
    if rpm -V -f %{_sysconfdir}/named.conf | egrep -q %{_sysconfdir}/named.conf; then
        dst=%{_sysconfdir}/named.conf.rpmsave.`/bin/date +'%Y-%m-%d_%H-%M-%S.%N'`
        echo "Saving %{_sysconfdir}/named.conf as $dst"
        mv %{_sysconfdir}/named.conf $dst
    fi

    cat << EOD >> $cf
###### start of updates from %{name}-%{version} package.
include "%{_sysconfdir}/named_raf.conf";
###### end of updates from %{name}-%{version} package.
EOD
fi

%if %{do_chroot}
if egrep -q '^ROOTDIR=' /etc/sysconfig/named; then
    bind-chroot-admin --sync
    source `which bind-chroot-admin -q`
    replace_with_link %{chroot_prefix}/%{_sysconfdir}/named_raf.conf \
         %{_sysconfdir}/named_raf.conf
    replace_with_link %{chroot_prefix}/%{_sysconfdir}/raf.ucar.edu.key \
         %{_sysconfdir}/raf.ucar.edu.key
fi
%endif

chkconfig --level 2345 named on

/etc/init.d/named restart

:;

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0640,root,named,0750)

# _localstatedir=/var.

# files are installed to /etc and /var/named
%if %{do_chroot}
# If %{do_chroot}, the triggerin script runs bind-chroot-admin,
# which moves files matching /etc/named.* and /var/named/*
# (along with /etc/named_raf.conf and /etc/raf.ucar.edu.key)
# to /var/named/chroot and creates links to them
# from /var/named and /etc.
# Hence the two directives for each file below:
%config %verify(not link) %{_sysconfdir}/named_raf.conf
%ghost  %config %{chroot_prefix}/etc/named_raf.conf
%config %verify(not link) /var/named/raf.ucar.edu
%ghost  %config %{chroot_prefix}/var/named/raf.ucar.edu
%config %verify(not link) /var/named/192.168.184
%ghost  %config %{chroot_prefix}/var/named/192.168.184
%config %verify(not link) /var/named/192.168.84
%ghost  %config %{chroot_prefix}/var/named/192.168.84
%else
%config %{_sysconfdir}/named_raf.conf
%config /var/named/raf.ucar.edu
%config /var/named/192.168.184
%config /var/named/192.168.84
%endif

%changelog
* Sun Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
