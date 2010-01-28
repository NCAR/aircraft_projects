#!/bin/sh

# echo "nargs=$#"
if [[ `id -un` == ads && ("$1" == ci || "$1" == commit) ]] && ! echo "$@" | fgrep -q -- --username; then
	read -p "enter --username for svn checkin: " uname
	\svn --username $uname "$@"
else
	\svn "$@"
fi
