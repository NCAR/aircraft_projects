#!/bin/sh
#
# This script removes the space from the filenames Cindy sent and then
# breaks the files into lines (they came over as the entire contents of
# the file on one line.

unzip ${DAT}/CVIDataroMerge.zip

mv ${DAT}/RF03DatatoMerge\ copy.txt ${DAT}/RF03DatatoMergecopy.txt
mv ${DAT}/RF08DatatoMerge\ copy.txt ${DAT}/RF08DatatoMergecopy.txt
mv ${DAT}/RF09DatatoMerge\ copy.txt ${DAT}/RF09DatatoMergecopy.txt
mv ${DAT}/RF10DatatoMerge\ copy.txt ${DAT}/RF10DatatoMergecopy.txt
mv ${DAT}/RF12DatatoMerge\ copy.txt ${DAT}/RF12DatatoMergecopy.txt
mv ${DAT}/RF14DatatoMerge\ copy.txt ${DAT}/RF14DatatoMergecopy.txt
mv ${DAT}/RF15DatatoMerge\ copy.txt ${DAT}/RF15DatatoMergecopy.txt

mac2unix ${DAT}/RF03DatatoMergecopy.txt
mac2unix ${DAT}/RF08DatatoMergecopy.txt
mac2unix ${DAT}/RF09DatatoMergecopy.txt
mac2unix ${DAT}/RF10DatatoMergecopy.txt
mac2unix ${DAT}/RF12DatatoMergecopy.txt
mac2unix ${DAT}/RF14DatatoMergecopy.txt
mac2unix ${DAT}/RF15DatatoMergecopy.txt
