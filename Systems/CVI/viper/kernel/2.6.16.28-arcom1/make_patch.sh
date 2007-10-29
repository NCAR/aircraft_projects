#!/bin/sh

cd linux-source-2.6.16.28-arcom1_pps
ael-kernel-build -architecture=arm clean
cd ..

diff -PruN --exclude="*.o" --exclude=".config" \
	--exclude="stamp-kernel-configure" --exclude=build.log \
	linux-source-2.6.16.28-arcom1-orig linux-source-2.6.16.28-arcom1_pps
