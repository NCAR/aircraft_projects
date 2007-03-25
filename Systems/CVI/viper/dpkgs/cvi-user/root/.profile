# ~/.profile: executed by bash(1) for login shells.

if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

PATH=/usr/local/bin:/usr/sbin:/sbin:$PATH

umask 022

export CVI=/root/cvi
[ -f $CVI/cvi_env.sh ] && source $CVI/cvi_env.sh

