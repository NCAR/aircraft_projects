#!/bin/sh

package=rsync
pkgdest=$PWD/../built/$package

PATH=/opt/arcom/bin:$PATH

[ -d rsync-2.6.8 ] || tar xzf rsync-2.6.8.tar.gz

cd rsync-2.6.8

./configure --host=arm-linux --prefix=$pkgdest

make

make install

make clean
