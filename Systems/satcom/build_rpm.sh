#!/bin/sh

if [ ! -d eol/repo/scripts ]; then
    svn co -N http://svn.eol.ucar.edu/svn/eol || exit 1
fi

pushd eol
svn update repo
popd

source eol/repo/scripts/repo_funcs.sh

topdir=`get_rpm_topdir`
rroot=`get_eol_repo_root`

pkg=raf-satcom
version=1.0
release=1
tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}

rpmbuild -ba --clean ${pkg}.spec

pkg=raf-ddclient
version=1.0
release=1
ddver=3.7.3

[ -d ${pkg}/usr/sbin ] || mkdir -p ${pkg}/usr/sbin
rm -rf /tmp/ddclient-${ddver}
tar xjf ddclient-${ddver}.tar.bz2 -C /tmp ddclient-${ddver}/ddclient
mv /tmp/ddclient-${ddver}/ddclient ${pkg}/usr/sbin
tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}
cp ddclient-mail-on-kill.patch ${topdir}/SOURCES

rpmbuild -ba --clean ${pkg}.spec

pkg=raf-satcom-mpds
version=1.0
release=1
tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}

rpmbuild -ba --clean ${pkg}.spec

pkg=raf-satcom-iridium
version=1.0
release=1
tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}

rpmbuild -ba --clean ${pkg}.spec

if [ -d $rroot ]; then
    rpms="$topdir/RPMS/noarch/raf-satcom-*.noarch.rpm $topdir/RPMS/noarch/raf-ddclient-*.noarch.rpm"
    copy_rpms_to_eol_repo $rpms
fi

