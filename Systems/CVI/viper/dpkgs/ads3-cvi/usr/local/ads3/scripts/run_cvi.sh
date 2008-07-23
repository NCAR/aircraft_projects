#!/bin/sh

if [ -z "$ADS3" -o -z "$PROJECT" -o -z "$AIRCRAFT" ]; then
    source /root/.profile
fi

dsm '$ADS3/projects/$PROJECT/$AIRCRAFT/nidas/cvi.xml'

