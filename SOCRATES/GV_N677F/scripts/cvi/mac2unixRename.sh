#!/bin/sh
#
# This script removes the space from the filenames Cindy sent and then
# breaks the files into lines (they came over as the entire contents of
# the file on one line.

unzip ${CVIDAT}/CVIDataroMerge.zip

mv ${CVIDAT}/RF03DatatoMerge\ copy.txt ${CVIDAT}/RF03DatatoMergecopy.txt
mv ${CVIDAT}/RF08DatatoMerge\ copy.txt ${CVIDAT}/RF08DatatoMergecopy.txt
mv ${CVIDAT}/RF09DatatoMerge\ copy.txt ${CVIDAT}/RF09DatatoMergecopy.txt
mv ${CVIDAT}/RF10DatatoMerge\ copy.txt ${CVIDAT}/RF10DatatoMergecopy.txt
mv ${CVIDAT}/RF12DatatoMerge\ copy.txt ${CVIDAT}/RF12DatatoMergecopy.txt
mv ${CVIDAT}/RF14DatatoMerge\ copy.txt ${CVIDAT}/RF14DatatoMergecopy.txt
mv ${CVIDAT}/RF15DatatoMerge\ copy.txt ${CVIDAT}/RF15DatatoMergecopy.txt

mac2unix ${CVIDAT}/RF03DatatoMergecopy.txt
mac2unix ${CVIDAT}/RF08DatatoMergecopy.txt
mac2unix ${CVIDAT}/RF09DatatoMergecopy.txt
mac2unix ${CVIDAT}/RF10DatatoMergecopy.txt
mac2unix ${CVIDAT}/RF12DatatoMergecopy.txt
mac2unix ${CVIDAT}/RF14DatatoMergecopy.txt
mac2unix ${CVIDAT}/RF15DatatoMergecopy.txt
