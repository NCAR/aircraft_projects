#!/bin/sh

cd etc
 
[ -d rc2.d ] || mkdir rc2.d

cd rc2.d
[ -L S20pcmcom8 ] || ln -s ../init.d/pcmcom8 S20pcmcom8
