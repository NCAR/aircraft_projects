#!/bin/sh

package=rsync
pkgdest=$PWD/../built/$package

PATH=/opt/arcom/bin:$PATH

[ -d rsync-2.6.9 ] || tar xzf rsync-2.6.9.tar.gz

cd rsync-2.6.9

./configure --host=arm-linux --prefix=$pkgdest

make

make install

make clean
