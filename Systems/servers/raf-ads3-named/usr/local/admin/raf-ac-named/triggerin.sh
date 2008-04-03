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
[ $# -ge 1 ] || usage

case $1 in
ac | lab)
    whichpkg=$1
    ;;
*)
    usage
    ;;
esac

SYSCONFDIR=${SYSCONFDIR:-/etc}
DO_CHROOT=${DO_CHROOT:-false}

cf=${SYSCONFDIR}/named.conf
if ! egrep -q '^[[:space:]]*include[[:space:]]+"${SYSCONFDIR}/named.${whichpkg}.conf"' $cf; then
    # use rpm -V to see if named.conf has been modified from the RPM
    if rpm -V -f ${SYSCONFDIR}/named.conf | egrep -q ${SYSCONFDIR}/named.conf; then
        dst=${SYSCONFDIR}/named.conf.rpmsave.`/bin/date +'%Y-%m-%d_%H-%M-%S.%N'`
        echo "Saving ${SYSCONFDIR}/named.conf as $dst"
        mv ${SYSCONFDIR}/named.conf $dst
    fi

    cat << EOD >> $cf
###### start of updates from %{name}-%{version} package.
include "${SYSCONFDIR}/named.${whichpkg}.conf";
###### end of updates from %{name}-%{version} package.
EOD
fi

# Copy named.loopback, named.localhost, named.empty to /var/named
# if they don't exist.  These were taken from caching-nameserver-9.4.2-3.fc7
# (which is also used in fc8). Earlier distributions had other files.
ad=/usr/local/admin/raf-ads3-named
pushd $ad > /dev/null
for f in named.*; do
    [ -f /var/named/$f ] || cp $f /var/named
done

# bind-chroot-admin moves all /etc/named.* and /var/named/* files to
# /var/named/chroot and links them back.
if $DO_CHROOT && egrep -q '^ROOTDIR=' /etc/sysconfig/named; then
    bind-chroot-admin --sync
fi

chkconfig --level 2345 named on

/etc/init.d/named restart

exit 0
