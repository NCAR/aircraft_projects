#!/bin/sh

package=cvi-user
pkgdest=../built/$package

[ -d $pkgdest ] || mkdir $pkgdest

rsync --exclude=.svn -a root DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

rm -rf $pkgdest


