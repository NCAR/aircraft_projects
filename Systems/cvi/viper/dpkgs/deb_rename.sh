#!/bin/sh

pkgdest=$1
d=`dirname $pkgdest`
f=`basename $pkgdest`
p=`dpkg -I $d/$f.deb | fgrep Package: | awk '{print $2}'`
v=`dpkg -I $d/$f.deb | fgrep Version: | awk '{print $2}'`
a=`dpkg -I $d/$f.deb | fgrep Architecture: | awk '{print $2}'`


if [ -n "$a" -a "$a" != "all" ]; then
    new=$d/${p}_${v}_${a}.deb
else
    new=$d/${p}_${v}.deb
fi

mv $d/$f.deb $new
echo "package: $new"
