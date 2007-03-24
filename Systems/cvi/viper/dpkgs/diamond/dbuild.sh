#!/bin/sh

# Build the diamond package.
#
# This package contains the driver modules
# dmd_mmat.ko and short_filters, copied from
# /opt/nidas/arm/linux, so make sure they are up-to-date
# or otherwise are the version you want to put in the diamond
# package.

set -x

kernel=2.6.16.28-arcom1-2-viper

package=diamond
pkgdest=../built/$package

[ -d $pkgdest ] || mkdir -p $pkgdest

moddir=lib/modules/$kernel/extra
[ -d $moddir ] || mkdir -p $moddir
cp /opt/nidas/arm/linux/dmd_mmat.ko $moddir
cp /opt/nidas/arm/linux/short_filters.ko $moddir

./rc_symlinks.sh

rsync --exclude=.svn -a etc lib DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

# rm -rf $pkgdest
