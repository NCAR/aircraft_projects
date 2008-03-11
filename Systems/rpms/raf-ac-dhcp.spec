Summary: DHCP configuration for RAF aircraft server
Name: raf-ac-dhcp
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch
Requires: dhcp
Source: %{name}-%{version}.tar.gz

%description
DHCP configuration for RAF aircraft server

%prep
%setup -n %{name}

%build

%install
install -d $RPM_BUILD_ROOT%{_sysconfdir}
cp -r etc/* $RPM_BUILD_ROOT%{_sysconfdir}

%triggerin -- dhcp
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# The dhcp package owns /etc/dhcpd.conf, so we must edit it
# in the triggerin script.  The default file just has a comment
# refering to /usr/share/doc/dhcp*/dhcpd.conf.sample

# Append an include of dhcpd-raf-ac.conf if needed.
cf=%{_sysconfdir}/dhcpd.conf
if ! egrep -q '^[[:space:]]*include[[:space:]]+"%{_sysconfdir}/dhcpd-raf-ac.conf"' $cf; then
    # use rpm -V to see if dhcpd.conf has been modified from the RPM
    if rpm -V -f %{_sysconfdir}/dhcpd.conf | egrep -q %{_sysconfdir}/dhcpd.conf; then
        dst=%{_sysconfdir}/dhcpd.conf.rpmsave.`/bin/date +'%Y-%m-%d_%H-%M-%S.%N'`
        echo "Saving %{_sysconfdir}/dhcpd.conf as $dst"
        mv %{_sysconfdir}/dhcpd.conf $dst
    fi

    cat << EOD >> $cf
###### start of updates from %{name}-%{version} package.
include "%{_sysconfdir}/dhcpd-raf-ac.conf";
###### end of updates from %{name}-%{version} package.
EOD
fi

# Create the key for dynamic updates from dhcpd to named.
# If we called it /etc/named.raf.key, then /bin/sbin/bind-chroot-admin
# will find it, moving files called /etc/named.* to /var/named/chroot and
# creates the links back to /etc.
cf=%{_sysconfdir}/raf.ucar.edu.key
if [ ! -e $cf ]; then
    cd /var/named
    dnssec-keygen -a HMAC-MD5 -b 128 -n HOST raf.ucar.edu > /dev/null
    cat << EOD > $cf
key raf.ucar.edu {
    algorithm hmac-md5;
    secret "`awk '{print $7}' Kraf.ucar.edu.*.key | sed 's/==$//'`";
};
EOD
fi
# rm -f Kraf.ucar.edu.*

[ -e $cf ] && chown root:named $cf
[ -e $cf ] && chmod 0640 $cf

chkconfig --level 2345 dhcpd on

/etc/init.d/dhcpd restart

exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-raf-ac.conf
%config %attr(0644,root,root) %{_sysconfdir}/dhcpd-dsms.conf
%ghost %config %attr(0640,root,named) %verify(not link) %{_sysconfdir}/raf.ucar.edu.key

%changelog
* Thu Mar  6 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
