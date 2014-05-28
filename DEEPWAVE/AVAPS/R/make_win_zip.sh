#!/bin/sh

zipfile=$PWD/deepwave_R.zip
rm -f $zipfile

echo $zipfile

tmpdir=$(mktemp -d /tmp/mkzip_XXXXXX)
trap "{ rm -rf $tmpdir; }" EXIT

cp *.R $tmpdir
cp windows/* $tmpdir
cp windows/.Rprofile $tmpdir

cd $tmpdir
zip $zipfile * .Rprofile

echo "zip file: $zipfile"

