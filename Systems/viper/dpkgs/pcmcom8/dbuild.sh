#!/bin/sh

# Build the pcmcom8 package.
#
# This package contains the driver module pcmcom8.ko, which is copied
# from /opt/local/nidas/arm/linux, so make sure it is up-to-date
# or otherwise is the version you want to put in the pcmcom8
# package.

set -x

kernel=2.6.16.28-arcom1-2-viper

pkg=pcmcom8
pkgdest=../built/$pkg

[ -d $pkgdest ] || mkdir -p $pkgdest

rm -rf lib/modules
moddir=lib/modules/$kernel/extra
[ -d $moddir ] || mkdir -p $moddir
cp /opt/local/nidas/arm/linux/pcmcom8.ko $moddir

bindir=bin
[ -d $bindir ] || mkdir -p $bindir
cp /opt/local/nidas/arm/bin/set_pcmcom8 $bindir

./rc_symlinks.sh

rsync --exclude=.svn -a etc bin lib DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/${pkg}.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest

kernel=2.6.16.21-ael1-2-vulcan
arch=armbe

rm -rf lib/modules
moddir=lib/modules/$kernel/extra
[ -d $moddir ] || mkdir -p $moddir
cp /opt/local/nidas/armbe/linux/pcmcom8.ko $moddir

bindir=bin
[ -d $bindir ] || mkdir -p $bindir
cp /opt/local/nidas/armbe/bin/set_pcmcom8 $bindir

./rc_symlinks.sh

rsync --exclude=.svn -a etc bin lib DEBIAN $pkgdest
sed -e "s/^Architecture:.*/Architecture: $arch/" DEBIAN/control > $pkgdest/DEBIAN/control

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/${pkg}.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest

rm -rf bin lib
