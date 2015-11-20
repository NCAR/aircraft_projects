################################################################################
#                                                                              #
# /net/adm/etc/System.cshrc		                                       #
# Major clean-up SN 8 mar 02
# Version 2.0 SN Sep 2003
# Version 2.1 SN /usr/local replaced by /net/local_lnx (linux)
# Version 2.2 SN got rid of ifconfig net code,
# moved out default printer code                                               #
# This file should be sourced by all ATD C shells.                             #
#                                                                              #
################################################################################

#
#   Determine which operating system and network is being used
#

export HOST=`uname -n`
export LANG=C

#
# Linux
#
# This is for support of Motif applications.
# See: http://ubuntuforums.org/showthread.php?t=82087
export XKEYSYMDB=/usr/share/X11/XKeysymDB

export PATH=/usr/kerberos/bin:/bin:/usr/bin:/usr/X11R6/bin:/opt/local/bin

echo $-
if [ -z "$USER" ]; then exit; fi
if [[ $- != *i* ]]; then exit; fi

#
# System-wide/other environment variables
#
set ignoreeof=1
set -o noclobber
export EDITOR=vim
export PAGER=less
unset TMOUT
umask 002
ulimit -c unlimited

export HISTCONTROL=ignoredups:erasedups	# no duplicate entries
export HISTSIZE=1000			# big big history
export HISTFILESIZE=10000		# big big history
shopt -s histappend			# append to history, don't overwrite it

alias help="man man"
alias h='history | more '
alias ..='set dot=$cwd ; cd ..'
alias ,='set dot=$cwd ; cd $dot '
alias lss='ls -Fal \!* | sort -r +3 | more'
alias ll='ls -la \!* | more'
alias lg='ls -lag \!* | more'
alias lt='ls -alt \!* | more'

echo end system
