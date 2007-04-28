#!/bin/sh

cd linux-source-2.6.11.11-arcom1
ael-kernel-build -architecture=arm clean > /dev/null 2>&1
cd ..

diff -PruN --exclude="*.o" --exclude "*.ko" --exclude "*.mod.c" \
    --exclude=".config" --exclude="stamp-kernel-configure" \
    linux-source-2.6.11.11-arcom1_orig \
    linux-source-2.6.11.11-arcom1
