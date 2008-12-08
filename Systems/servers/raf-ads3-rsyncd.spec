Summary: Configuration for rsyncd on ADS3 server systems.
Name: raf-ads3-rsyncd
Version: 1.0
Release: 3
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Requires: rsync xinetd

%description
Configuration for rsyncd on ADS3 server systems to provide downloads
of nidas software.

%triggerin -- rsync selinux-policy
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

chkconfig --level 5 xinetd || chkconfig --level 2345 xinetd on

# enable rsync in xinetd
disabled=`awk '/disable/{print $3}' /etc/xinetd.d/rsync`

hupxinetd=false
if [ "$disabled" != no ]; then
    sed -ri 's/disable[[:space:]]+=[[:space:]]*.*/disable    = no/' /etc/xinetd.d/rsync
    hupxinetd=true
fi

# add
#   only_from = 192.168.0.0/16 127.0.0.1
# to xinetd.d/rsync.  We already restrict to these hosts in /etc/rsyncd.conf,
# so this is not critical. To avoid overwriting what is otherwise wanted,
# add an "only_from" if it is not already found in /etc/xinetd.d/rsync.
# Warn the installer if an only_from exists and doesn't contain 192.168.0.0/16.
#
# Also suppress logging of successfull connects with log_on_success = <nothing>
if fgrep -q only_from /etc/xinetd.d/rsync; then
    if ! fgrep only_from /etc/xinetd.d/rsync | fgrep -q 192.168.0.0/16; then
        echo "Warning: /etc/xinet.d/rsync has an \"only_from\" statement that does not include 192.168.0.0/16"
    fi
else
    sed -ri '/disable[[:space:]]+=/a \
        only_from = 192.168.0.0/16 127.0.0.1\
        log_on_success =' /etc/xinetd.d/rsync
    hupxinetd=true
fi

if $hupxinetd; then
    pkill -HUP xinetd || /etc/init.d/xinetd start
else
    pgrep xinetd > /dev/null || /etc/init.d/xinetd start
fi

if ! { [ -f /etc/rsyncd.conf ] && fgrep -q nidas-arm /etc/rsyncd.conf; }; then
    cat >> /etc/rsyncd.conf << EOD
[nidas-arm]
    comment = nidas binaries, libraries and firmware for arm
    path = /opt/local/nidas/arm
    read only = true
    use chroot = false
    hosts allow = 127.0.0.1 192.168.0.0/16
    log file = /dev/null

[nidas-armbe]
    comment = nidas binaries, libraries and firmware for armbe
    path = /opt/local/nidas/armbe
    read only = true
    use chroot = false
    hosts allow = 127.0.0.1 192.168.0.0/16
    log file = /dev/null

[ael-dpkgs]
    comment = Debian packages for Arcom Embedded Linux
    path = /opt/local/ael-dpkgs
    read only = true
    use chroot = false
    hosts allow = 127.0.0.1 192.168.0.0/16
    log file = /dev/null
EOD
fi

# see man rsync_selinux
if selinuxenabled; then
    echo "setting up SELinux permissions on /opt/local/nidas"
    [ -d /opt/local/nidas ] || mkdir -p /opt/local/nidas
    chcon -R -t public_content_t /opt/local/nidas
    # [ -f /etc/selinux/config ] && . /etc/selinux/config
    # sef=/etc/selinux/$SELINUXTYPE/contexts/files/file_contexts.local
    # if ! { [ -f $sef ] && fgrep -q /opt/local/nidas $f; }; then
    #     echo "/opt/local/nidas(/.*)? system_u:object_r:public_content_t:s0" >> $sef
    # fi
    if ! semanage fcontext -l -t public_content_t | fgrep -q /opt/local/nidas; then
        semanage fcontext -a -t public_content_t "/opt/local/nidas(/.*)?"
    fi
    echo "setting up SELinux permissions on /opt/local/ael-dpkgs"
    [ -d /opt/local/ael-dpkgs/ads3 ] || mkdir -p /opt/local/ael-dpkgs/ads3
    chcon -R -t public_content_t /opt/local/ael-dpkgs
    if ! semanage fcontext -l -t public_content_t | fgrep -q /opt/local/ael-dpkgs; then
        semanage fcontext -a -t public_content_t "/opt/local/ael-dpkgs(/.*)?"
    fi
fi

exit 0

%postun
if selinuxenabled; then
    semanage fcontext -d -t public_content_t "/opt/local/nidas(/.*)?"
    restorecon /opt/local/nidas
    semanage fcontext -d -t public_content_t "/opt/local/ael-dpkgs(/.*)?"
    restorecon /opt/local/ael-dpkgs
fi

%files

%changelog
* Mon Dec 8 2008 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Added only_from in xinetd.d/rsync, suppressed logging
* Wed Dec 3 2008 Gordon Maclean <maclean@ucar.edu> 1.0-2
- added /opt/local/ael-dpkgs
* Wed Nov 19 2008 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial version
