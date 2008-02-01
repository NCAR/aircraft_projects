#!/bin/sh

pkg=rsync
pkgdest=../built/$pkg

rsync --exclude=.svn -a DEBIAN $pkgdest

# nuke man pages
rm -rf $pkgdest/man

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/${pkg}.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest
