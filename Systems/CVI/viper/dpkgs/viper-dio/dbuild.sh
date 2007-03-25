#!/bin/sh

# Build the viper-dio package.
#
# This package contains the driver module viper_dio
# copied from /opt/nidas/arm/linux, so make sure it is up-to-date
# or otherwise are the version you want to put.

set -x

kernel=2.6.16.28-arcom1-2-viper

package=viper-dio
pkgdest=../built/$package

[ -d $pkgdest ] || mkdir -p $pkgdest

moddir=lib/modules/$kernel/extra
[ -d $moddir ] || mkdir -p $moddir
cp /opt/nidas/arm/linux/viper_dio.ko $moddir

./rc_symlinks.sh

rsync --exclude=.svn -a etc lib DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

# rm -rf $pkgdest
