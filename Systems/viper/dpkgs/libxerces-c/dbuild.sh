#!/bin/sh

package=libxerces-c
pkgdest=../built/$package

rm -rf $pkgdest/usr/include
rm -rf $pkgdest/usr/lib/libxerces-depdom*

rsync --exclude=.svn -a DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

# rm -rf $pkgdest
