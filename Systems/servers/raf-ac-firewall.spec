Summary: Iptables configuration for RAF aircraft server
Name: raf-ac-firewall
Version: 1.0
Release: 7
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# BuildRoot is only needed by older rpm versions
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
# initscripts gives /etc/sysctl.conf, procps gives /sbin/sysctl
Requires: iptables initscripts procps
Source: %{name}-%{version}.tar.gz

%description
Iptables configuration for RAF aircraft server.

%prep
%setup -n %{name}

%build

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/usr/local/admin
install -d $RPM_BUILD_ROOT/etc/sysconfig
cp -r usr/local/admin/raf-ac-firewall $RPM_BUILD_ROOT/usr/local/admin
cp -r etc/sysconfig/iptables $RPM_BUILD_ROOT/etc/sysconfig

%triggerin -- iptables initscripts
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# turn on forwarding
cf=/etc/sysctl.conf
if ! egrep -q "^[[:space:]]*net.ipv4.ip_forward=" $cf; then
    echo "net.ipv4.ip_forward=1" >> $cf
else
sed -i -c '/^[[:space:]]*net.ipv4.ip_forward=/{
s/=0/=1/
}' $cf
fi
if [ `sysctl -n net.ipv4.ip_forward` == 0 ]; then
    sysctl net.ipv4.ip_forward=1
fi

# run the iptables-setup.sh script
# convert counters in lines like ":PREROUTING ACCEPT [20971:4859482]" to 0:0
# otherwise they will always differ
/usr/local/admin/raf-ac-firewall/iptables-setup.sh | sed -r "s/^(:[^[]+\[)[0-9]+:[0-9]+/\10:0/" > /tmp/iptables.$$
cd /etc/sysconfig
if ! diff -q --ignore-matching-lines="^#" /tmp/iptables.$$ iptables > /dev/null; then
    echo "Saving `pwd`/iptables as `pwd`/iptables.rpmsave"
    mv iptables iptables.rpmsave
    mv /tmp/iptables.$$ iptables
    rm -f iptables.rpmnew
fi
rm -f /tmp/iptables.$$

# add necessary modules for iptables
cf=/etc/sysconfig/iptables-config
sed -i -c '/^[[:space:]]*IPTABLES_MODULES=/{
/ip_conntrack_ftp/b
s/IPTABLES_MODULES="[^"]*/& ip_conntrack ip_conntrack_ftp/
}' $cf

sed -i -c '/^[[:space:]]*IPTABLES_MODULES=/{
/iptable_nat/b
s/IPTABLES_MODULES="[^"]*/& iptable_nat/
}' $cf

if ! { chkconfig --list iptables | fgrep -q "5:on"; }; then
    chkconfig --level 2345 iptables on
fi
/etc/init.d/iptables restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%config(noreplace) %attr(0600,root,root) /etc/sysconfig/iptables
%dir /usr/local/admin/raf-ac-firewall
%config %attr(0755,root,root) /usr/local/admin/raf-ac-firewall/iptables-setup.sh

%changelog
* Fri Apr 20 2012 Gordon Maclean <maclean@ucar.edu> 1.0-7
- Added support for udp port forwarding.
- In iptables-setup.sh, exit on error, clearing out firewall.
- Use piece of /etc/init.d/iptables to load modules.
* Wed Oct 26 2011 Gordon Maclean <maclean@ucar.edu> 1.0-6
- Simplified VPN rules, allowing protocol esp, and udp ports
- isakmp,ipsec-nat-t, and 10000. Added tun+ as a SAFE_EXT_ISF
* Thu May  5 2011 Gordon Maclean <maclean@ucar.edu> 1.0-5
- Removed IP addresses for GOOGLE_EARTH. Trying to block those accesses isn't working.
* Wed May  4 2011 Gordon Maclean <maclean@ucar.edu> 1.0-4
- Removed entry to log CLAMP-MSS packets. Not needed, and probably
- didn't actually log the packets whose MSS was changed anyway.
* Mon Jul 26 2010 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Allow ICMP type=3 out. Logs showed rejects of these from named to forwarding
- nameservers. They seem harmless to enable.
* Fri Apr 11 2008 Gordon Maclean <maclean@ucar.edu>
- changed googleearth filtering
* Sun Feb 29 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
