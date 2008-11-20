Summary: Configuration for rsyncd on ADS3 server systems.
Name: raf-ads3-rsyncd
Version: 1.0
Release: 1
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

if [ "$disabled" != no ]; then
    sed -ri 's/disable[[:space:]]+=[[:space:]]*.*/disable    = no/' /etc/xinetd.d/rsync
    pkill -HUP xinetd || /etc/init.d/xinetd start
else
    pgrep xinetd > /dev/null || /etc/init.d/xinetd start
fi

if ! { [ -f /etc/rsyncd.conf ] && fgrep -q nidas-arm /etc/rsyncd.conf; }; then
    cat >> /etc/rsyncd.conf << EOD
[nidas-arm]
    comment = nidas binaries, libraries and firmware for arm
    path = /opt/local/nidas/arm
    syslog facility = daemon
    read only = true
    use chroot = false
    hosts allow = 127.0.0.1 192.168.0.0/16

[nidas-armbe]
    comment = nidas binaries, libraries and firmware for armbe
    path = /opt/local/nidas/armbe
    syslog facility = daemon
    read only = true
    use chroot = false
    hosts allow = 127.0.0.1 192.168.0.0/16
EOD
fi

# see man rsync_selinux
if selinuxenabled; then
    echo "setting up SELinux permissions on /opt/local/nidas"
    chcon -R -t public_content_t /opt/local/nidas
    # [ -f /etc/selinux/config ] && . /etc/selinux/config
    # sef=/etc/selinux/$SELINUXTYPE/contexts/files/file_contexts.local
    # if ! { [ -f $sef ] && fgrep -q /opt/local/nidas $f; }; then
    #     echo "/opt/local/nidas(/.*)? system_u:object_r:public_content_t:s0" >> $sef
    # fi
    if ! semanage fcontext -l -t public_content_t | fgrep -q /opt/local/nidas; then
        semanage fcontext -a -t public_content_t "/opt/local/nidas(/.*)?"
    fi
fi

exit 0

%postun
if selinuxenabled; then
    semanage fcontext -d -t public_content_t "/opt/local/nidas(/.*)?"
    restorecon /opt/local/nidas
fi

%files

%changelog
* Wed Nov 19 2008 Gordon Maclean <maclean@ucar.edu>
- initial version

