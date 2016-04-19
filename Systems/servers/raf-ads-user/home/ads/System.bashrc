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

export PATH=/bin:/usr/bin:/usr/X11R6/bin:/opt/local/bin

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

alias help='man man'
alias h='history | $PAGER'
alias ..='cd ..'
alias ,='cd $OLDPWD'
function lss() { ls -Fal "$@" | sort -r +3 | $PAGER ;}
function ll() { ls -la "$@" | $PAGER ;}
function lg() { ls -lag "$@" | $PAGER ;}
function lt() { ls -alt "$@" | $PAGER ;}
