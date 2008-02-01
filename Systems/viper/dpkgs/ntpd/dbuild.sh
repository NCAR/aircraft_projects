#!/bin/sh

pkg=ntpd
pkgdest=../built/$pkg

./rc_symlinks.sh
rm -rf $pkgdest/DEBIAN
rm -rf $pkgdest/etc
rsync --exclude=.svn -a etc DEBIAN $pkgdest

chmod -R g-ws $pkgdest/usr
chmod -R g-ws $pkgdest/etc
chmod -R g-ws $pkgdest/DEBIAN

# nuke stuff not needed on the viper
rm -rf $pkgdest/usr/man
rm -f $pkgdest/usr/sbin/ntpdc
rm -f $pkgdest/usr/sbin/sntp
rm -f $pkgdest/usr/bin/ntp-keygen
rm -f $pkgdest/usr/bin/ntptrace
rm -f $pkgdest/usr/bin/ntp-wait
rm -f $pkgdest/usr/bin/tickadj

fakeroot dpkg -b $pkgdest

dpkg-name ${pkgdest%/*}/${pkg}.deb

mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

rm -rf $pkgdest
