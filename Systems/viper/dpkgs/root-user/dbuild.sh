#!/bin/sh

package=root-user
pkgdest=../built/$package

[ -d $pkgdest ] || mkdir -p $pkgdest

rsync --exclude=.svn -a root DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

rm -rf $pkgdest


