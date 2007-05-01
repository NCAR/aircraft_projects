#!/bin/sh

package=cvi-user
pkgdest=../built/$package

./rc_symlinks.sh

[ -d $pkgdest ] || mkdir $pkgdest

rsync --exclude=.svn -a root etc DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

rm -rf $pkgdest


