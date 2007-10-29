#!/bin/sh

tar xzf linux-source-2.6.16.28-arcom1.tar.gz

cd linux-source-2.6.16.28-arcom1

patch -p1 < ../viper_autoclr_pps.patch

make ARCH=arm viper_defconfig

cp ../config .config

make ARCH=arm CROSS_COMPILE=arm-linux- LOCALVERSION=-arcom1-2-viper oldconfig

# Need make zImage and make modules in case a source file has changed
# since last build. ael-kernel-build doesn't detect and compile
# changed source files.
make ARCH=arm CROSS_COMPILE=arm-linux- LOCALVERSION=-arcom1-2-viper zImage

make ARCH=arm CROSS_COMPILE=arm-linux- LOCALVERSION=-arcom1-2-viper modules

ael-kernel-build --arch=arm --append-to-version=-2-viper --revision=autoclrpps.1 image
