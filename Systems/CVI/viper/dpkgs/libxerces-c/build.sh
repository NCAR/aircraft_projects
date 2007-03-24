#!/bin/sh

package=libxerces-c
pkgdest=$PWD/../built/$package

if [ ! -d xerces-c-src_2_7_0 ]; then
    tar xzf xerces-c-current.tar.gz
fi

cd xerces-c-src_2_7_0 || exit 1

# Patch runConfigure so that it accepts arm-linux-g++.
patch -p 1 < ../runConfigure.patch

export XERCESCROOT=$PWD
cd $XERCESCROOT/src/xercesc

PATH=/opt/arcom/bin:$PATH

# which arm-linux-g++

# Then build it:

export CXXFLAGS="-O2"
export CFLAGS="-O2"

# build dpkg
./runConfigure -p linux -c arm-linux-gcc -x arm-linux-g++ -C --host=arm-linux -C --prefix=$pkgdest/usr
make
make install

./runConfigure -p linux -c arm-linux-gcc -x arm-linux-g++ -C --host=arm-linux -C --prefix=/opt/nidas/arm
make
make install

make distclean

# Building for X86
./runConfigure -p linux -c gcc -x g++ -C --prefix=/opt/nidas/x86
make
make install
make distclean

