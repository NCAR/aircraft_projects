#!/bin/sh

pkg=etc-files
pkgdest=../built/$pkg

rm -rf $pkgdest

for arch in arm armbe; do

    ./rc_symlinks.sh

    [ -d $pkgdest ] || mkdir -p $pkgdest

    rsync --exclude=.svn -a etc DEBIAN $pkgdest
    rm $pkgdest/etc/fstab.v*
    rm $pkgdest/etc/dsm_modules.conf.v*
    case $arch in
    arm)
        rsync etc/fstab.viper $pkgdest/etc/fstab
        rsync etc/dsm_modules.conf.viper $pkgdest/etc/dsm_modules.conf
        ;;
    armbe)
        rsync etc/fstab.vulcan $pkgdest/etc/fstab
        rsync etc/dsm_modules.conf.vulcan $pkgdest/etc/dsm_modules.conf
        ;;
    esac
    sed -e "s/^Architecture:.*/Architecture: $arch/" DEBIAN/control > $pkgdest/DEBIAN/control

    fakeroot dpkg -b $pkgdest

    dpkg-name ${pkgdest%/*}/$pkg.deb

    mv ${pkgdest%/*}/${pkg}_*.deb /net/www/docs/software/ael-dpkgs

    rm -rf $pkgdest
done
