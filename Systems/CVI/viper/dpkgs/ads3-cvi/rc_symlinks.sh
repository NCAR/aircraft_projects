#!/bin/sh

cd etc
 
[ -d rc0.d ] || mkdir rc0.d
[ -d rc1.d ] || mkdir rc1.d
[ -d rc2.d ] || mkdir rc2.d
[ -d rc6.d ] || mkdir rc6.d

cd rc0.d
[ -L K01cvi ] || ln -s ../init.d/cvi K01cvi

cd ../rc1.d
[ -L K01cvi ] || ln -s ../init.d/cvi K01cvi

cd ../rc6.d
[ -L K01cvi ] || ln -s ../init.d/cvi K01cvi

cd ../rc2.d
[ -L S99cvi ] || ln -s ../init.d/cvi S99cvi
