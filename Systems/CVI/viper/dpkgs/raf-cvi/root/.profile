# ~/.profile: executed by bash(1) for login shells.

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

umask 022

PATH=/usr/local/bin:/usr/sbin:/sbin:$PATH

export ADS3=/usr/local/ads3

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
[ -f $pf ] || echo "$pf not found. Cannot setup project environment."
source $pf

# export CVI=/root/cvi
# [ -f $CVI/cvi_env.sh ] && source $CVI/cvi_env.sh

