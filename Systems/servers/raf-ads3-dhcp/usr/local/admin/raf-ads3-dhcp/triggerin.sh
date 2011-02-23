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
    type=ac
    achost=$1
    ;;
lab)
    type=$1
    ;;
*)
    usage
    ;;
esac
pkg=$2

SYSCONFDIR=${SYSCONFDIR:-/etc}
cf=dhcpd.conf
# new versions of dhcp package put config file on /etc/dhcp
if [ -f $SYSCONFDIR/dhcp/$cf ]; then
    cf=$SYSCONFDIR/dhcp/$cf
else
    cf=$SYSCONFDIR/$cf
fi

# Append an include of dhcpd-ac.conf if needed.
if ! egrep -q '^[[:space:]]*include[[:space:]]+"'$SYSCONFDIR/dhcp/dhcpd-ac.conf\" $cf; then
    # use rpm -V to see if dhcpd.conf has been modified from the RPM
    if rpm -V -f $cf | egrep -q $cf; then
        if [ -e $cf ]; then
            dst=${cf}.rpmsave.`/bin/date +'%Y-%m-%d_%H-%M-%S.%N'`
            echo "Saving $cf as $dst"
            mv $cf $dst
        fi
    fi

    if [ $type == ac ]; then
        cat << EOD >> $cf
###### start of updates from ${pkg} package.
include "$SYSCONFDIR/dhcp/dhcpd-ac.conf";
include "$SYSCONFDIR/dhcp/dhcpd-${achost}.conf";
include "$SYSCONFDIR/dhcp/dhcpd-dsms.conf";
#
# Put local, temporary changes in /etc/dhcp/dhcpd-local.conf,
# which is not saved under Subversion and is not part
# of an RPM.
include "$SYSCONFDIR/dhcp/dhcpd-local.conf";
###### end of updates from ${pkg} package.
EOD
    else
        cat << EOD >> $cf
###### start of updates from ${pkg} package.
include "$SYSCONFDIR/dhcp/dhcpd-lab.conf";
include "$SYSCONFDIR/dhcp/dhcpd-dsms.conf";
#
# Put local, temporary changes in /etc/dhcp/dhcpd-local.conf,
# which is not saved under Subversion and is not part
# of an RPM.
include "$SYSCONFDIR/dhcp/dhcpd-local.conf";
###### end of updates from ${pkg} package.
EOD
    fi
fi

# Create the key for dynamic updates from dhcpd to named.
# If we called it /etc/named.raf.key, then /bin/sbin/bind-chroot-admin
# would find it, moving files called /etc/named.* to /var/named/chroot and
# creates the links back to /etc.
# We don't plan to use bind-chroot-admin, so we'll call it raf.ucar.edu.key
#
# Using dnssec-keygen -b 128 caused "bad base64 encoding error for named"
# dnssec-keygen -b 512 worked.
# 
cf=${SYSCONFDIR}/raf.ucar.edu.key
Kf=(/var/named/Kraf.ucar.edu.*.private)

# More than one Kraf file, somethings fishy
[ ${#Kf[*]} -ne 1 ] && rm -f ${Kf[*]}

# keys don't agree
if [ -e $cf -a -e ${Kf[0]} ]; then
    key="`awk '/^Key:/{print $2}' ${Kf[0]}`"
    fgrep -q "$key" $cf || rm -f $cf
fi

if [ ! -e $cf -o ! -e ${Kf[0]} ]; then
    /etc/init.d/named stop
    cd /var/named
    rm -f Kraf.ucar.edu.*
    dnssec-keygen -a HMAC-MD5 -b 512 -n HOST raf.ucar.edu > /dev/null || exit 1
    # Leave the Kraf.ucar.edu.* files on /var/named for possible nsupdate uses
    cat << EOD > $cf
key raf.ucar.edu {
    algorithm hmac-md5;
    secret "`awk '/^Key:/{print $2}' Kraf.ucar.edu.*.private`";
};
EOD
    # If you recreate the key, nuke the named .jnl files. It might prevent the
    # "Unable to add forward map from blah.blah to blah.blah: timed out"
    # dhcpd error.
    rm -rf /var/named/*.jnl
    /etc/init.d/named start
fi

[ -e $cf ] && chown root:named $cf
[ -e $cf ] && chmod 0640 $cf

# Create empty dhcpd-local file if it doesn't exist
cf=${SYSCONFDIR}/dhcp/dhcpd-local.conf
cfold=${SYSCONFDIR}/dhcpd-local.conf
# move old one
[ ! -e $cf -a -e $cfold ] && mv $cfold $cf
[ -e $cf ] || touch $cf

if ! { chkconfig --list dhcpd | fgrep -q "5:on"; }; then
    chkconfig --level 2345 dhcpd on
fi

/etc/init.d/dhcpd restart

exit 0
