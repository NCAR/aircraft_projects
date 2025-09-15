#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 flight1 flight2 flight3 ..."
    echo "Example: $0 rf06 rf07 rf08"
    exit 1
fi

# Create template if it doesn't exist (one-time setup)
if [ ! -f ../movieParamFile.template ]; then
    cp ../movieParamFile ../movieParamFile.template
fi

for FLIGHT in "$@"; do
    echo "Processing flight: $FLIGHT"

    # Create movieParamFile from template, replacing rf00 with current flight
    sed "s/rf00/$FLIGHT/g" ../movieParamFile.template > ../movieParamFile
    
    # Run the movie creation
    /net/jlocal/projects/scripts/camera/combineCameras.pl ../movieParamFile $FLIGHT
    
    echo "Completed flight: $FLIGHT"
done
