#!/bin/sh

exec > ./merge_dgps_h.log 2>&1

for destfile in `ls -1 /scr/raf/Prod_Data/DEEPWAVE/DEEPWAVE*h.nc`
do
    srcfile=`echo $destfile | sed 's/DEEPWAVE\(....\)h.nc/..\/MERGE\/DGPS\/\1_dgps.nc/'`
    if [ -f "$srcfile" ]; then
        echo "Merge $srcfile into $destfile"
        ncmerge -v GGLAT_DGPS,GGLON_DGPS,GGALT_DGPS,GGLONSD_DGPS,GGLATSD_DGPS,GGALTSD_DGPS,GGVEW_DGPS,GGSVNS_DGPS,GGVSPD_DGPS $destfile $srcfile
    else
	ncfillvar -v GGLAT_DGPS,GGLON_DGPS,GGALT_DGPS,GGLONSD_DGPS,GGLATSD_DGPS,GGALTSD_DGPS,GGVEW_DGPS,GGSVNS_DGPS,GGVSPD_DGPS -c GGLAT $destfile
        echo "Add blank DGPS to $destfile"
    fi

    echo "Edit attributed for $destfile"
    ncatted -O -a units,GGALTSD_DGPS,m,c,"m" $destfile
    ncatted -O -a long_name,GGALTSD_DGPS,m,c,"Standard Deviation of DGPS Geopotential Altitude" $destfile
    ncatted -O -a units,GGLATSD_DGPS,m,c,"degree_N"  $destfile
    ncatted -O -a long_name,GGLATSD_DGPS,m,c,"Standard Deviation of DGPS Latitude"  $destfile
    ncatted -O -a units,GGLONSD_DGPS,m,c,"degree_E"  $destfile
    ncatted -O -a long_name,GGLONSD_DGPS,m,c,"Standard Deviation of DGPS Longitude" $destfile
    ncatted -O -a units,GGSVNS_DGPS,m,c,"m/s"  $destfile
    ncatted -O -a long_name,GGSVNS_DGPS,m,c,"GPS Ground Speed Vector, North Component"  $destfile
    ncatted -O -a units,GGVSPD_DGPS,m,c,"m/s"  $destfile
    ncatted -O -a long_name,GGVSPD_DGPS,m,c,"GPS Vertical Speed"  $destfile

    ncatted -O -a units,GGALTSD_DGPS,c,c,"m" $destfile
    ncatted -O -a long_name,GGALTSD_DGPS,c,c,"Standard Deviation of DGPS Geopotential Altitude" $destfile
    ncatted -O -a units,GGLATSD_DGPS,c,c,"degree_N"  $destfile
    ncatted -O -a long_name,GGLATSD_DGPS,c,c,"Standard Deviation of DGPS Latitude"  $destfile
    ncatted -O -a units,GGLONSD_DGPS,c,c,"degree_E"  $destfile
    ncatted -O -a long_name,GGLONSD_DGPS,c,c,"Standard Deviation of DGPS Longitude" $destfile
    ncatted -O -a units,GGSVNS_DGPS,c,c,"m/s"  $destfile
    ncatted -O -a long_name,GGSVNS_DGPS,c,c,"GPS Ground Speed Vector, North Component"  $destfile
    ncatted -O -a units,GGVSPD_DGPS,c,c,"m/s"  $destfile
    ncatted -O -a long_name,GGVSPD_DGPS,c,c,"GPS Vertical Speed"  $destfile

    ncrename -O -v GGSVNS_DGPS,GGVNS_DGPS $destfile

    ncatted -O -a units,GGLAT_DGPS,c,c,"degree_N" $destfile
    ncatted -O -a long_name,GGLAT_DGPS,c,c,"DGPS Latitude" $destfile
    ncatted -O -a units,GGLON_DGPS,c,c,"degree_E" $destfile
    ncatted -O -a long_name,GGLON_DGPS,c,c,"DGPS Longitude" $destfile
    ncatted -O -a units,GGALT_DGPS,c,c,"m" $destfile
    ncatted -O -a long_name,GGALT_DGPS,c,c,"DGPS Geopotential Altitude" $destfile
    ncatted -O -a units,GGVEW_DGPS,c,c,"m/s" $destfile
    ncatted -O -a long_name,GGVEW_DGPS,c,c,"DGPS Ground Speed Vector, East Component" $destfile
    ncatted -O -a units,GGVNS_DGPS,c,c,"m/s" $destfile
    ncatted -O -a long_name,GGVNS_DGPS,c,c,"GPS Ground Speed Vector, North Component" $destfile
    ncatted -O -a long_name,GGVSPD_DGPS,c,c,"DGPS Vertical Speed" $destfile

    ncatted -O -a units,GGLAT_DGPS,m,c,"degree_N" $destfile
    ncatted -O -a long_name,GGLAT_DGPS,m,c,"DGPS Latitude" $destfile
    ncatted -O -a units,GGLON_DGPS,m,c,"degree_E" $destfile
    ncatted -O -a long_name,GGLON_DGPS,m,c,"DGPS Longitude" $destfile
    ncatted -O -a units,GGALT_DGPS,m,c,"m" $destfile
    ncatted -O -a long_name,GGALT_DGPS,m,c,"DGPS Geopotential Altitude" $destfile
    ncatted -O -a units,GGVEW_DGPS,m,c,"m/s" $destfile
    ncatted -O -a long_name,GGVEW_DGPS,m,c,"DGPS Ground Speed Vector, East Component" $destfile
    ncatted -O -a units,GGVNS_DGPS,m,c,"m/s" $destfile
    ncatted -O -a long_name,GGVNS_DGPS,m,c,"GPS Ground Speed Vector, North Component" $destfile
    ncatted -O -a long_name,GGVSPD_DGPS,m,c,"DGPS Vertical Speed" $destfile

    # Remove history 
    ncatted -a history,global,d,c, $destfile
done
