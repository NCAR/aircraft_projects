#!/bin/sh

make  ARCH=arm CROSS_COMPILE=armbe-linux- LOCALVERSION=-arcom1-2-vulcan zImage
make  ARCH=arm CROSS_COMPILE=armbe-linux- LOCALVERSION=-arcom1-2-vulcan modules
ael-kernel-build --arch=armbe --append-to-version=-2-vulcan --revision=1 image
