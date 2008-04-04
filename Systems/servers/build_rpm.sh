#!/bin/sh

script=`basename $0`

source ../satcom/repo_scripts/repo_funcs.sh

dopkg=all
[ $# -gt 0 ] && dopkg=$1

topdir=`get_rpm_topdir`
rroot=`get_eol_repo_root`

log=/tmp/$script.$$
trap "{ rm -f $log; }" EXIT

set -o pipefail

pkg=raf-ac-firewall
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=1.0
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    # rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    rpmbuild -ba ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ac-ntp
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=1.0
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-lab-ntp
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=1.0
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-syslog
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=1.0
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-dhcp
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=1.0
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-named
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=1.0
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

echo "RPMS:"
egrep "^Wrote:" $log

if [ -d $rroot ]; then
    rpms="$topdir/RPMS/noarch/raf-*.noarch.rpm"
    for r in $rpms; do
        echo $r
    done
    # copy_rpms_to_eol_repo $rpms
fi

