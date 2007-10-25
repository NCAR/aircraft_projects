#!/bin/sh

package=etc-files
pkgdest=../built/$package

./rc_symlinks.sh

[ -d $pkgdest ] || mkdir -p $pkgdest

rsync --exclude=.svn -a etc DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

rm -rf $pkgdest
