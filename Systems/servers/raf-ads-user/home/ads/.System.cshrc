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

setenv HOST     `uname -n`
setenv LANG C

switch (`uname`)
   case SunOS:
      setenv MYOS Solaris
   breaksw

   case Linux:
      setenv MYOS Linux
   breaksw

   default:
      setenv MYOS unknown
   breaksw
endsw

#
# Set up the environment according to which OS we're running.
#

switch ( $MYOS )
#
# Solaris
#
    case Solaris:
	set path=( /usr/bin /usr/sbin /usr/local/bin \
		/usr/dt/bin /usr/openwin/bin )

	setenv MANPATH /usr/share/man:/usr/local/man:/usr/openwin/man
	setenv LD_LIBRARY_PATH /usr/dt/lib:/usr/openwin/lib:/usr/local/lib:/usr/local/X11R6/lib
	setenv XKEYSYMDB /usr/openwin/lib/XKeysymDB
	setenv XAPPLRESDIR /usr/openwin/lib/app-defaults:/usr/local/lib/app-defaults
	setenv XFILESEARCHPATH /usr/lib/X11/%T/%N:/usr/openwin/lib/%T/%N%S:/usr/openwin/lib/locale/%L/%T/%N%S

	# use kilobyte-style output for df and du in Solaris
	alias   df      'df -k'
	alias   du      'du -k'
    breaksw
#
# Linux
#
    case Linux:
#	echo "System.cshrc thinks I'm running Linux"
#	SN - feb08- figure out if it's RHEL or CentOS 5
# grep returns a 0 if there is a match, hence complement the logic
	grep "release 4" /etc/redhat-release > /dev/null
	set rhel4 = $status
	if ! $rhel4 then
		setenv XKEYSYMDB /usr/lib/X11/XKeysymDB
	else
		setenv XKEYSYMDB /usr/share/X11/XKeysymDB
	endif

	set path=( /usr/kerberos/bin /bin /usr/bin /usr/X11R6/bin \
	/opt/local/bin /net/local_lnx/bin)
	setenv IDL_DIR /net/csoft_lnx/itt/idl
	
     breaksw
#
# None of the above
#
    default:
	echo "System.cshrc does not know which OS is being run: $MYOS, paths not set."
    breaksw
endsw

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
# place stty commands in System.login
#stty sane
# The following is commented until a global ATD-wide locate database can be
# implemented...  MDD 2/6/02
#alias locate "locate -d /usr/local/var/locatedb"

alias help	"man man"
alias h		'history | more '
alias ..	'set dot=$cwd ; cd ..'
alias ,		'set dot=$cwd ; cd $dot '
alias lss	'ls -Fal \!* | sort -r +3 | more'
alias ll	'ls -la \!* | more'
alias lg	'ls -lag \!* | more'
alias lt	'ls -alt \!* | more'

#
##The following chunk sets the prompt
#
if ($USER == root ) then
 set prompt="`uname -n`:$cwd \!# "
 alias cd 'set dot=$cwd; chdir \!* ; set prompt="`uname -n`:$cwd \! # "'

else if ( $MYOS == Linux && !($?NO_PROMPT) ) then
 set prompt="`hostname `:$cwd \!% "
 alias cd 'set dot=$cwd; chdir \!* ; set prompt="%m:%~ %h%% "'

else if ( !($?NO_PROMPT) ) then
 set prompt="`uname -n`:$cwd \!% "
 alias cd 'set dot=$cwd; chdir \!* ; set prompt="`uname -n`:$cwd \! % "'
endif


#
	set HN=`uname -n | awk -F'.' '{print $1}'`

	switch ( `basename $shell` )
	    case csh:
		if ( !($?NO_PROMPT) ) then
                   if ($USER == root) then
		      alias cwdcmd 'set prompt="\! `echo $HN`:$cwd # "'
                   else
		      alias cwdcmd 'set prompt="\! `echo $HN`:$cwd-> "'
                   endif
		   cwdcmd
		   alias cd 'cd \!* ; cwdcmd'
		   alias popd 'popd ; cwdcmd'
		   alias pushd 'pushd \!* ; cwdcmd'
		endif
		set filec
	    breaksw
	    case tcsh:
		unset autologout
		set nobeep
		if ( !($?NO_PROMPT) ) then
                   if ($USER == root) then
		      alias cwdcmd 'set prompt="\! `echo $HN`:$cwd # "'
                   else
		      alias cwdcmd 'set prompt="\! `echo $HN`:$cwd-> "'
                   endif
		   cwdcmd
		   alias cd 'cd \!* ; cwdcmd'
		   alias popd 'popd ; cwdcmd'
		   alias pushd 'pushd \!* ; cwdcmd'
		endif
	    breaksw
	endsw
endif


#if ( -f /etc/motd ) then
#   cat /etc/motd
#endif


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
