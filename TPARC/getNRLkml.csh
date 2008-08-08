#!/bin/csh
set tclist = "012 013"
set sensorlist = "37rgb 85rgb"

cd /space/tmp/NRLkml
set baseURL = "http://www.nrlmry.navy.mil/archdat/test/kml/TC/2008/WPAC"
# We have to pull each file individually, since 
foreach tc ($tclist)
    mkdir -p $tc
    pushd $tc
    foreach sensor ($sensorlist)
	mkdir -p $sensor
	pushd $sensor
	# Get the index, which contains a list of files available
	set index = "tmp_index.html"
	wget -O$index ${baseURL}/$tc/$sensor/kml

	# Extract the names of the kml files from the index, and grab each one
	# along with its associated png file
	set kmlfiles = `cat $index | sed 's/<[^>]*>//g' | awk '{ print $1; }' | fgrep kml`
	foreach kml ($kmlfiles)
	    # skip the tile files (which contain ".11.", ".12.", ".21.", 
	    # or ".22." in the file name)
	    echo $kml | grep -q -e "\.[12][12]\."
	    if ($? == 0) then
#		echo "SKIPPING $kml"
		continue
	    endif

	    if (! -f $kml) then
		set png = `echo $kml | sed 's/kml/png/g'`
		wget ${baseURL}/$tc/$sensor/kml/$kml
		wget ${baseURL}/$tc/$sensor/kml/$png
	    endif
	end
	rm $index
	popd
    end
    popd
end
