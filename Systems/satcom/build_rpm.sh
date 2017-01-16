#!/bin/sh

if grep -q Fedora /etc/redhat-release; then
    echo "Error: noarch RPMs built on Fedora seem to be incompatible with RHEL"
    echo "Until this is resolved, do this build on a RHEL system."
    echo "/etc/redhat-release = $(</etc/redhat-release)"
    echo "rpmbuild --version = " `rpmbuild --version`
    # exit 1
fi

script=`basename $0`

usage() {
    echo "$script [-i] [dpkg]"
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

# set pipefail shell option so that
# rpmbuild | tee || exit $? will exit if rpmbuild fails
set -o pipefail

pkg=raf-satcom
if [ $dopkg == all -o $dopkg == $pkg ]; then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}
    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-ddclient
if [ $dopkg == all -o $dopkg == $pkg ]; then
    version=`get_version $pkg.spec`
    ddver=3.7.3

    [ -d ${pkg}/usr/sbin ] || mkdir -p ${pkg}/usr/sbin
    rm -rf /tmp/ddclient-${ddver}
    tar xjf ddclient-${ddver}.tar.bz2 -C /tmp ddclient-${ddver}/ddclient
    mv /tmp/ddclient-${ddver}/ddclient ${pkg}/usr/sbin
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}
    cp ddclient-mail-on-kill.patch ${topdir}/SOURCES

    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-satcom-mpds
if [ $dopkg == all -o $dopkg == $pkg ]; then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}

    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-satcom-iridium
if [ $dopkg == all -o $dopkg == $pkg ]; then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}

    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

pkg=raf-satcom-bgan
if [ $dopkg == all -o $dopkg == $pkg ]; then
    version=`get_version $pkg.spec`
    tar czf ${topdir}/SOURCES/${pkg}-${version}.tar.gz --exclude .svn ${pkg}

    rpmbuild -ba --clean ${pkg}.spec | tee -a $log  || exit $?
fi

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

