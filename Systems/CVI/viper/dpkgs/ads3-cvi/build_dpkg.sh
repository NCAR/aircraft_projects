#!/bin/sh

dpkg=ads3-cvi

nidas=/opt/local/nidas

tmpdir=/tmp/dbuild_$$
pdir=$tmpdir/$dpkg
[ -d $pdir ] || mkdir -p $pdir
trap "{ rm -rf $tmpdir; }" EXIT

rsync --exclude=.svn -a DEBIAN etc $pdir

[ -d $pdir/usr/local/bin ] || mkdir -p $pdir/usr/local/bin
[ -d $pdir/usr/local/lib ] || mkdir -p $pdir/usr/local/lib
[ -d $pdir/usr/local/stamps ] || mkdir -p $pdir/usr/local/stamps

chmod -R g-ws $pdir/DEBIAN
chmod -R g-ws $pdir/etc
chmod -R g-ws $pdir/usr/local/bin
chmod -R g-ws $pdir/usr/local/lib

rsync -a $nidas/arm/lib/libnidas.so $pdir/usr/local/lib
rsync -a $nidas/arm/lib/libnidas_dynld.so $pdir/usr/local/lib

stampfile=$pdir/usr/local/stamps/${dpkg}.stamp
dv=`awk /^Version:/'{print $2}' DEBIAN/control`
sv=`$nidas/x86/bin/dsm -v`	# nidas subversion version
d=`TZ=UTC date +%Y%m%d%H%M%S`
echo "$dv $sv $d" > $stampfile
echo -n "Stamp file: " | cat - $stampfile

apps=(dsm data_stats data_dump rserial ck_xml)
for app in ${apps[*]}; do
    rsync -a $nidas/arm/bin/$app $pdir/usr/local/bin
done

# Currently we don't copy any nidas driver modules. Those are in their
# own packages, like the diamond package

fakeroot dpkg -b $pdir
# ../deb_rename.sh $pkgdest
dpkg-name ${pdir%/*}/${dpkg}.deb

www1=/var/www/html/software/ael-dpkgs 
www2=/net/www/docs/software/ael-dpkgs 

if [ -d $www1 ]; then
    www=$www1
elif [ -d $www2 ]; then
    www=$www2
else
    echo "$www1 or $www2 not found"
    www=/tmp
fi

[ -d $www/ads3 ] || mkdir -p $www/ads3

shopt -s nullglob
df=(${pdir%/*}/${dpkg}*_{arm,all}.deb)
df=${df[0]}
echo $df
echo moving $df to $www/ads3
mv $df $www/ads3 || exit 1
cp $stampfile $www/ads3/${dpkg}.stamp
