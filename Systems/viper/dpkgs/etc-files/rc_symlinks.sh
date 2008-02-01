#!/bin/sh

cd etc
 
[ -d rc2.d ] || mkdir rc2.d
[ -d rc6.d ] || mkdir rc6.d

cd rc2.d
[ -L S99ads3 ] || ln -s ../init.d/ads3 S99ads3

cd ../rc6.d
[ -L K01ads3 ] || ln -s ../init.d/ads3 K01ads3
