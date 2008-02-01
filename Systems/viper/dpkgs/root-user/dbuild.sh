#!/bin/sh

pkg=root-user
pkgdest=../built/$pkg

[ -d $pkgdest ] || mkdir -p $pkgdest

rsync --exclude=.svn -a root DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/${pkg}.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest


