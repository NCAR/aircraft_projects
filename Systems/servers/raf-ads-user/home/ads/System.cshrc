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

setenv HOST	`uname -n`
setenv LANG	C

#
# Linux
#
# This is for support of Motif applications.
# See: http://ubuntuforums.org/showthread.php?t=82087
setenv XKEYSYMDB /usr/share/X11/XKeysymDB

set path=( /usr/kerberos/bin /bin /usr/bin /usr/X11R6/bin \
	/opt/local/bin )


if ($?USER == 0 || $?prompt == 0) exit
#echo "System.cshrc interactive..."

#
# System-wide/other environment variables
#
set ignoreeof
set filec
set history = 100
set savehist = 25
set noclobber
setenv EDITOR   emacs
setenv PAGER less
unset autologout
umask 002
limit coredumpsize 0k

alias help	"man man"
alias h		'history | more '
alias ..	'set dot=$cwd ; cd ..'
alias ,		'set dot=$cwd ; cd $dot '
alias lss	'ls -Fal \!* | sort -r +3 | more'
alias ll	'ls -la \!* | more'
alias lg	'ls -lag \!* | more'
alias lt	'ls -alt \!* | more'

#
# The following chunk sets the prompt
#
# Removed prompt stuff.  CJW.
#

#
# This sets a DISPLAY env var, useful for Exceed users on DHCP
#
tty >/dev/null
if (! $status) then
   env | grep DISPLAY >/dev/null
   if ($status) then
      if ( `uname` == Linux ) then
         set hname=`who -m --lookup | head -n 1 | awk -F\( '{print $2}' | sed 's/)//'`
      else if ( `uname` == SunOS ) then
         set hname=`who -m | head -n 1 | awk -F\( '{print $2}' | sed 's/)//'`
      else
         echo "System.cshrc: Unrecognized OS, uname = `uname`"
         exit (0)
      endif
     setenv DISPLAY ${hname}:0
   endif
endif
