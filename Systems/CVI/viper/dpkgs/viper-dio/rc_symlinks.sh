#!/bin/sh

cd etc
 
[ -d rc2.d ] || mkdir rc2.d

cd rc2.d
[ -L S95viper_dio ] || ln -s ../init.d/viper_dio S95viper_dio
