#!/bin/csh
@ defMaxSize = 50000

if ($# < 1 || $# > 2) then
    echo "Shrink an image until it is smaller than max_size bytes (default $defMaxSize),"
    echo "The new image created will have the same name as the source image, with prefix"
    echo "'tiny_' prepended."
    echo
    echo "Usage: $0 [<max_size>] img_file"
    exit 1
endif

if ($# == 2) then
    @ maxSize = $1
    set infile = "$2"
else
    @ maxSize = $defMaxSize
    set infile = "$1"
endif

set head = "${infile:h}"
set tail = "${infile:t}"
if ($tail == $infile) then
    set outfile = "tiny_$infile"
else
    set outfile = "$head/tiny_$tail"
endif
cp $infile $outfile

@ maxScale = 100
@ step = 5
@ minScale = $step
@ scale = 50
@ size = `ls -l $outfile | cut -d' ' -f5`

while (1)
    echo -n ".."
    convert -depth 8 -colors 32 -scale ${scale}% $infile $outfile

    @ size = `ls -l $outfile | cut -d' ' -f5`
    echo -n "$size (${scale}%)"
    if ($maxScale == $minScale) break

    if ($size < $maxSize) then
	@ minScale = $scale
    else
	@ maxScale = $scale - $step
    endif

    # If the allowed bounds zeroed in on the scale we just did, get out now
    if (($minScale == $maxScale) && ($scale == $minScale)) break

    @ scale = ($maxScale + $minScale + $step) / 2
    @ scale = ($scale / $step) * $step
end
echo

if ($size > $maxSize) then
    echo "Cannot scale smaller than $size (${scale}%)"
    rm $outfile
    exit 1
endif
echo "Scaled to $size (${scale}%)"
