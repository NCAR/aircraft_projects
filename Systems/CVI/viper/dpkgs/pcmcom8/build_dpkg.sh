#!/bin/sh

# Build the diamond package.
#
# This package contains the driver modules dmd_mmat.ko,
# short_filters.ko and nidas_util.ko, copied from
# /opt/local/nidas/arm/linux, so make sure they are up-to-date
# or otherwise are the version you want to put in the diamond
# package.

# set -x

dpkg=pcmcom8

mods=(pcmcom8.ko)

# location of nidas tree
nidas=/opt/local/nidas

# Get kernel version from value of vermagic= in a driver module
kernel=`strings $nidas/arm/linux/${mods[0]} | \
	awk '/vermagic=/{print $1}' | sed 's/.*=//'`

echo "kernel=$kernel"

tmpdir=/tmp/dbuild_$$
pdir=$tmpdir/$dpkg
[ -d $pdir ] || mkdir -p $pdir
trap "{ rm -rf $tmpdir; }" EXIT

moddir=$pdir/lib/modules/$kernel/extra
[ -d $moddir ] || mkdir -p $moddir

echo -n "copying modules from $nidas/arm/linux: "

for m in ${mods[*]}; do
    echo -n "$m "
    cp $nidas/arm/linux/$m $moddir
done
echo ""

bindir=$pdir/bin
[ -d $bindir ] || mkdir -p $bindir
cp $nidas/arm/bin/set_pcmcom8 $bindir

rsync --exclude=.svn -a etc DEBIAN $pdir
[ -d $pdir/usr/local/stamps ] || mkdir -p $pdir/usr/local/stamps

chmod -R g-ws $pdir/etc
chmod -R g-ws $pdir/DEBIAN
chmod -R g-ws $pdir/usr

stampfile=$pdir/usr/local/stamps/${dpkg}.stamp
dv=`awk /^Version:/'{print $2}' DEBIAN/control`
sv=`$nidas/x86/bin/dsm -v`	# nidas subversion version
d=`TZ=UTC date +%Y%m%d%H%M%S`
echo "$dv $sv $d" > $stampfile
echo -n "Stamp file: " | cat - $stampfile

fakeroot dpkg -b $pdir
rm -f ${pdir%/*}/${dpkg}-*.deb
dpkg-name ${pdir%/*}/${dpkg}.deb

www1=/var/www/html/software/ael-dpkgs 
www2=/net/www/docs/software/ael-dpkgs 

if [ -d $www1 ]; then
    www=$www1
elif [ -d $www2 ]; then
    www=$www2
else
    www=/tmp
    echo "$www1 or $www2 not found, copying file to $www"
fi

shopt -s nullglob
df=(${pdir%/*}/${dpkg}*_{arm,all}.deb)
df=${df[0]}
echo moving $df to $www/ads3
[ -d $www/ads3 ] || mkdir -p $www/ads3
mv $df $www/ads3 || exit 1
cp $stampfile $www/ads3/${dpkg}.stamp
