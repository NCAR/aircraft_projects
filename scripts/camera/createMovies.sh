#!/bin/csh

FLIGHT="rf01"

./net/jlocal/projects/scripts/camera/combineCameras.pl ../movieParamFile $FLIGHT
#TODO: Update createMovies.sh to be in only one location -- either project specific scripts folder or general scripts folder