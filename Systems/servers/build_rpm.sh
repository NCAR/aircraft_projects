#!/bin/sh

if grep -q Fedora /etc/redhat-release; then
    echo "Error: noarch RPMs built on Fedora seem to be incompatible with RHEL"
    echo "Until this is resolved, do this build on a RHEL system."
    echo "/etc/redhat-release = $(</etc/redhat-release)"
    echo "rpmbuild --version = " `rpmbuild --version`
    exit 1
fi

script=`basename $0`

if [ "$1" = "-h" -o "$1" = "--help" ]; then
    echo "$script [-i] [dpkg ...]"
    echo "-i: install RPM on EOL yum repository (if accessible)"
    exit 1
fi

doinstall=false

case $1 in
-i)
    doinstall=true
    shift
    ;;
esac

source repo_scripts/repo_funcs.sh

get_version () {
    awk '/^Version:/{print $2}' $1
}

topdir=`get_rpm_topdir`
rroot=`get_eol_repo_root`

log=/tmp/$script.$$
trap "{ rm -f $log; }" EXIT

# set pipefail shell option so that
# rpmbuild | tee || exit $? will exit if rpmbuild fails
set -o pipefail


dopkg=all

while [ "$dopkg" == all -o $# -gt 0 ]; do

    if [ $# -gt 0 ]; then
        echo "only building: $1"
        dopkg=$1
        shift
    fi

    pkg=raf-ads-user
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -bb ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-catalog
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -bb ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-gv
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-c130
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-nfs
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-firewall
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-nagios
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-chrony
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-gdm
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-selinux
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-ntp
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-lab-ntp
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ads3-syslog
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-avaps
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-mtp
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-postgresql
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ac-laptop
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ads3-sysctl
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ads3-dhcp
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ads3-named
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ads3-lab
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-ads3-sudoers
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    # jQuery for control, camera, and MC pages.
    pkg=raf-jquery
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" ${pkg}
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    # Mission Coordinator Web Interface RPMS
    pkg=raf-www-camera
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" raf-www/camera
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-www-control
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" raf-www/control
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    pkg=raf-www-map
    if [ "$dopkg" == all -o "$dopkg" == $pkg ];then
        version=`get_version $pkg.spec`
        tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn --exclude "*.swp" raf-www/flight_data
        rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
    fi

    dopkg=""

done

echo "RPMS:"
egrep "^Wrote:" $log
rpms=`egrep '^Wrote:' $log | egrep /RPMS/ | awk '{print $2}'`

if $doinstall; then
    if [ -d $rroot ]; then
        echo "Moving rpms to $rroot"
        move_rpms_to_eol_repo $rpms
    else
        echo "$rroot not found. Leaving RPMS in $topdir"
    fi
else
    echo "-i option not specified, RPMs will not be installed in $rroot"
fi
