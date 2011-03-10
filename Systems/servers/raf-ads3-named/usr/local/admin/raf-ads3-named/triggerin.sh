#!/bin/sh

# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# The bind package owns /etc/named.conf, so we must edit it
# in the triggerin script.

# Append an include of named.ac.conf if needed.

usage() {
    echo "Usage: $0 ac|lab packagename"
    exit 1
}

# whichpkg is ac or lab
[ $# -ge 2 ] || usage

case $1 in
ac | lab)
    whichpkg=$1
    ;;
*)
    usage
    ;;
esac
pkg=$2

SYSCONFDIR=${SYSCONFDIR:-/etc}
DO_CHROOT=${DO_CHROOT:-0}

cf=${SYSCONFDIR}/named.conf
# If there isn't an include of our named.{ac,lab}.conf in named.conf
# save the old and create a new one.
if ! grep -E -q '^[[:space:]]*include[[:space:]]+"'${SYSCONFDIR}/named.${whichpkg}.conf'"' $cf; then
    dst=${SYSCONFDIR}/named.conf.rpmsave.`/bin/date +'%Y-%m-%d_%H-%M-%S.%N'`
    echo "Saving ${SYSCONFDIR}/named.conf as $dst"
    mv ${SYSCONFDIR}/named.conf $dst

    cat << EOD > $cf
###### start of updates from $pkg package.
include "${SYSCONFDIR}/named.${whichpkg}.conf";
###### end of updates from $pkg package.
EOD
fi

own=`ls -ld /var/named | awk '{print $3$4}'`
if [ "$own" != rootnamed ]; then
    chown root.named /var/named
fi
perm=`ls -ld /var/named | awk '{print $1}'`
if [ "$perm" != "drwxrwx---" ]; then
    chmod 770 /var/named
fi

[ -d /var/named/log ] || mkdir /var/named/log
chgrp -R named /var/named/log
chmod -R g+w /var/named/log

# SELinux requires this
if selinuxenabled; then
    setsebool -P named_write_master_zones=1
fi

# Copy named.loopback, named.localhost, named.empty, named.ip6.local to /var/named
# if they don't exist.  These were taken from caching-nameserver-9.4.2-3.fc7
# (which is also used in fc8). Earlier distributions had other files.
ad=/usr/local/admin/raf-ads3-named
pushd $ad > /dev/null
for f in named.*; do
    if [ ! -f /var/named/$f ]; then
        cp $f /var/named
        chgrp named /var/named/$f
        chmod g+w /var/named/$f
    fi
done

# bind-chroot-admin moves all /etc/named.* and /var/named/* files to
# /var/named/chroot and links them back.
if [ $DO_CHROOT -ne 0 ]; then
    if [ grep -q '^ROOTDIR=' /etc/sysconfig/named; then
        bind-chroot-admin --sync
    fi
else
    sed -i 's/^ROOTDIR=/# ROOTDIR=/' /etc/sysconfig/named
fi

if ! { chkconfig --list named | fgrep -q "5:on"; }; then
    chkconfig --level 2345 named on
fi

# in bind-9.3.6-16.P1.el5 the rndc key in /etc/rndc.key was called rndckey
# in bind-9.7.0-5.P2.el6_0.1.i686 the rndc key is called rndc-key 
# We'll do a sed on /etc/rdnc.key and change the name to rndc-key
cf=/etc/rndc.key
if [ -f $cf ]; then
    grep -q rndc-key $cf || sed -i s/rndckey/rndc-key/ $cf
fi



/etc/init.d/named restart

exit 0
