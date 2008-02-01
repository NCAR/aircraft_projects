#!/bin/sh

pkg=libxerces-c
pkgdest=../built/$pkg

rm -rf $pkgdest/usr/include
rm -rf $pkgdest/usr/lib/libxerces-depdom*

rsync --exclude=.svn -a DEBIAN $pkgdest

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/${pkg}.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest
