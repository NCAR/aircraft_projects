#!/bin/sh

# echo "nargs=$#"
if [ "$1" == ci -o "$1" == commit ] && ! echo "$@" | fgrep -q -- --username; then
	read -p "enter --username for svn checkin: " uname
	svn --username $uname "$@"
else
	svn "$@"
fi
