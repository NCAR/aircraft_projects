#!/bin/sh

cd /etc
 
[ -d rc3.d ] || mkdir rc3.d
[ -d rc6.d ] || mkdir rc6.d

cd rc3.d
[ -L S99ads3 ] || ln -s ../init.d/ads3 S99ads3

cd ../rc6.d
[ -L K01ads3 ] || ln -s ../init.d/ads3 K01ads3
