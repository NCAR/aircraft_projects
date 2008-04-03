#!/bin/sh

# This is the triggerin script that is part of the raf-gv-dhcp and
# raf-c130-dhcp packages.
# It is run when the raf-gv-dhcp or raf-c130-dhcp packages are installed
# or updated, and when dhcp is installed or updated.
#
# Recommend: don't edit this script, change the RPMs and do a yum update.
#
# The dhcp package owns /etc/dhcpd.conf, so we must edit it
# in the triggerin script.  The default file just has a comment
# refering to /usr/share/doc/dhcp*/dhcpd.conf.sample

usage() {
    echo "Usage: $0 gv|c130 packagename"
    exit 1
}

# host is gv or c130
[ $# -ge 2 ] || usage

case $1 in
gv | c130)
    achost=$1
    ;;
*)
    usage
    ;;
esac
pkg=$2

SYSCONFDIR=${SYSCONFDIR:-/etc}

# Append an include of dhcpd-ac.conf if needed.
cf=${SYSCONFDIR}/dhcpd.conf
if ! egrep -q '^[[:space:]]*include[[:space:]]+"${SYSCONFDIR}/dhcpd-ac.conf"' $cf; then
    # use rpm -V to see if dhcpd.conf has been modified from the RPM
    if rpm -V -f ${SYSCONFDIR}/dhcpd.conf | egrep -q ${SYSCONFDIR}/dhcpd.conf; then
        dst=${SYSCONFDIR}/dhcpd.conf.rpmsave.`/bin/date +'%Y-%m-%d_%H-%M-%S.%N'`
        if [ -e ${SYSCONFDIR}/dhcpd.conf ]; then
            echo "Saving ${SYSCONFDIR}/dhcpd.conf as $dst"
            mv ${SYSCONFDIR}/dhcpd.conf $dst
        fi
    fi

    cat << EOD >> $cf
###### start of updates from ${pkg} package.
include "${SYSCONFDIR}/dhcpd-ac.conf";
include "${SYSCONFDIR}/dhcpd-${achost}.conf";
include "${SYSCONFDIR}/dhcpd-dsms.conf";
#
# Put local, temporary changes in /etc/dhcpd-local.conf,
# which is not saved under Subversion and is not part
# of an RPM.
include "${SYSCONFDIR}/dhcpd-local.conf";
###### end of updates from ${pkg} package.
EOD
fi

# Create the key for dynamic updates from dhcpd to named.
# If we called it /etc/named.raf.key, then /bin/sbin/bind-chroot-admin
# would find it, moving files called /etc/named.* to /var/named/chroot and
# creates the links back to /etc.
# We don't plan to use bind-chroot-admin, so we'll call it raf.ucar.edu.key
cf=${SYSCONFDIR}/raf.ucar.edu.key
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

# Create empty dhcpd-local file if it doesn't exist
cf=${SYSCONFDIR}/dhcpd-local.conf
[ -e $cf ] || touch $cf

chkconfig --level 2345 dhcpd on

/etc/init.d/dhcpd restart

exit 0
