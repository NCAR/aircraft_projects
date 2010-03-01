#!/bin/sh

script=`basename $0`

usage() {
    echo $script [-i]
    echo "-i: install RPM on EOL yum repository (if accessible)"
    exit 1
}

doinstall=false

case $1 in
-i)
    doinstall=true
    shift
    ;;
esac

dopkg=all
[ $# -gt 0 ] && dopkg=$1

source repo_scripts/repo_funcs.sh

get_version () {
    awk '/^Version:/{print $2}' $1
}

topdir=`get_rpm_topdir`
rroot=`get_eol_repo_root`

log=/tmp/$script.$$
trap "{ rm -f $log; }" EXIT

set -o pipefail

pkg=raf-ads-user
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -bb ${pkg}.spec | tee -a $log  || exit $?
fi

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
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ac-nagios
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
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
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-sysctl
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
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

pkg=raf-ads3-lab
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ads3-sudoers
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

# Mission Coordinator Web Interface RPMS
pkg=raf-www-camera
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" raf-www/camera
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-www-control
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" raf-www/control
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-www-map
if [ $dopkg == all -o $dopkg == $pkg ];then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" raf-www/flight_data
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

echo "RPMS:"
egrep "^Wrote:" $log
rpms=`egrep '^Wrote:' $log | egrep /RPMS/ | awk '{print $2}'`

if $doinstall; then
    if [ -d $rroot ]; then
        echo "Moving rpms to $rroot"
        copy_rpms_to_eol_repo $rpms
    else
        echo "$rroot not found. Leaving RPMS in $topdir"
    fi
else
    echo "-i option not specified, RPMs will not be installed in $rroot"
fi
