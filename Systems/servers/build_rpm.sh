#!/bin/sh

script=`basename $0`

source repo_scripts/repo_funcs.sh

get_version () {
    awk '/^Version:/{print $2}' $1
}

dopkg=all
[ $# -gt 0 ] && dopkg=$1

topdir=`get_rpm_topdir`
rroot=`get_eol_repo_root`

log=/tmp/$script.$$
trap "{ rm -f $log; }" EXIT

set -o pipefail

pkg=raf-gv
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-c130
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ac-firewall
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    # rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    rpmbuild -ba ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ac-ntp
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-lab-ntp
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-syslog
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    set -x
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-dhcp
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-named
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi


if [ -d $rroot ]; then
    rpms="$topdir/RPMS/noarch/raf-*.noarch.rpm"
    for r in $rpms; do
        echo $r
    done
    copy_rpms_to_eol_repo $rpms > /dev/null
fi

echo "RPMS:"
egrep "^Wrote:" $log
