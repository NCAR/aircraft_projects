#!/bin/sh

cd etc
 
[ -d rc2.d ] || mkdir rc2.d

cd rc2.d
[ -L S20emerald ] || ln -s ../init.d/emerald S20emerald
[ -L S95dmd_mmat ] || ln -s ../init.d/dmd_mmat S95dmd_mmat
