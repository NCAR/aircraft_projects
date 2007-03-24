#!/bin/sh

# Compile ntpd. Doesn't build the debian packate. Use dbuild.sh for that.

# dist=4.2.2p2
dist=4.2.4

# Copy timepps.h to cross tree
# cp pps/timepps.h /opt/arcom/arm-linux/include/timepps.h

if ! diff pps/timepps.h /opt/arcom/arm-linux/include/timepps.h; then
    cp pps/timepps.h /opt/arcom/arm-linux/include
fi

# install steps.  Not actually tested as a script.
# run by hand.

tar xzf ntp-$dist.tar.gz
cd ntp-$dist

# Apply PPS patch to nmea refclock
if patch -p1 --dry-run < ../pps/ntpd-nmea.patch; then
    patch -p1 < ../pps/ntpd-nmea.patch
fi

# cross compile for arm

PATH=/opt/arcom/bin:$PATH

package=ntpd
pkgdest=$PWD/../../built/$package

./configure --host=arm-linux --disable-all-clocks --disable-parse-clocks --enable-NMEA --enable-LOCAL-CLOCK --prefix=$pkgdest/usr --with-binsubdir=sbin

# Check that HAVE_PPSAPI is 1
grep HAVE_PPSAPI config.h || exit 1
make
make install
cd ..

cd pps
make CC=arm-linux-gcc
[ -d $pkgdest/bin ] || mkdir -p $pkgdest/bin
cp ppstest $pkgdest/bin
cd ..
