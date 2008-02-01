#!/bin/sh

pkg=etc-files
pkgdest=../built/$pkg

./rc_symlinks.sh

[ -d $pkgdest ] || mkdir -p $pkgdest

rsync --exclude=.svn -a etc DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/$pkg.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest
