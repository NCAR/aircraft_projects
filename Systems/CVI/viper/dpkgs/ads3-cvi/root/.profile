# ~/.profile: executed by bash(1) for login shells.

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

umask 022

export ADS3=/usr/local/ads3

PATH=/usr/local/bin:/usr/sbin:/sbin:$PATH:$ADS3/scripts

pf=$ADS3/current_project
if [ ! -f $pf ]; then
    echo "$pf not found. Cannot setup project environment."
    export PROJECT=unknown
else
    export PROJECT=$(<$pf)
fi

pf=$ADS3/current_aircraft
if [ ! -f $pf ]; then
    echo "$pf not found. Cannot setup AIRCRAFT environment."
    export AIRCRAFT=unknown
else
    export AIRCRAFT=$(<$pf)
fi

pf=$ADS3/projects/$PROJECT/$AIRCRAFT/scripts/dsm/cvi_env.sh
[ -f $pf ] && source $pf

export CDPATH=.:$ADS3/projects/$PROJECT/$AIRCRAFT


