#!/bin/sh

# Build the pcmcom8 package.
#
# This package contains the driver module pcmcom8.ko, which is copied
# from /opt/nidas/arm/linux, so make sure it is up-to-date
# or otherwise are the version you want to put in the pcmcom8
# package.

set -x

kernel=2.6.16.28-arcom1-2-viper

package=pcmcom8
pkgdest=../built/$package

[ -d $pkgdest ] || mkdir -p $pkgdest

moddir=lib/modules/$kernel/extra
[ -d $moddir ] || mkdir -p $moddir
cp /opt/nidas/arm/linux/pcmcom8.ko $moddir

bindir=bin
[ -d $bindir ] || mkdir -p $bindir
cp /opt/nidas/arm/bin/set_pcmcom8 $bindir

./rc_symlinks.sh

rsync --exclude=.svn -a etc bin lib DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

# rm -rf $pkgdest
