#!/bin/sh

package=rsync
pkgdest=../built/$package

rsync --exclude=.svn -a DEBIAN $pkgdest

# nuke man pages
rm -rf $pkgdest/man

fakeroot dpkg -b $pkgdest
../deb_rename.sh $pkgdest

# rm -rf $pkgdest
