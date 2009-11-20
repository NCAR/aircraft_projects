################################################################################
#                                                                              #
# /net/adm/etc/Jeffco_only.cshrc MDD 8/21/01                                   #
#                                                                              #
# SPECIAL NOTE: DO NOT MAKE MODIFICATIONS TO THIS FILE WITHOUT FIRST           #
# CONSULTING JEFFCO SOFTWARE DEVELOPERS!  Environment variables and other      #
# settings in this file are critical to the operation of the production        #
# aircraft data processing software at Jeffco.                                 #
#									       #
# The Systems Group does not mantain this file, it is really the domain	       #
# of the Jeffco SE's.							       #
#                                                                              #
# This file should be sourced by all JEFFCO C shells.                          #
#                                                                              #
################################################################################


setenv LOCAL /net/local_lnx
# next 3 lines moved from System.cshrc on 24Feb04 - SN
setenv PRINTER               raf-hp2300
setenv LPDEST                raf-hp2300

if ( $MYOS == Linux ) then
   setenv JLOCAL /opt/local
else if ( $MYOS == Solaris ) then
   setenv JLOCAL /jnet/solaris
endif

if (!($?PROJ_DIR)) then
   setenv PROJ_DIR /net/jlocal/projects
endif

if (!($?RAW_DATA_DIR)) then
   setenv RAW_DATA_DIR /scr/raf2/Raw_Data
endif

if (!($?DATA_DIR)) then
   setenv DATA_DIR /scr/jdata
endif

if (!($?PROD_DATA)) then
   setenv PROD_DATA /scr/productiondata
endif

# Commented out by Chris 09/09/03.
#setenv LD_LIBRARY_PATH  $JLOCAL/lib:${LD_LIBRARY_PATH}

################################################################################
# 3rd party software environment variables                                     #
################################################################################

# University Hawaii GMT package, used by ncplot geo-pol map.

setenv GMTHOME		$JLOCAL/GMT

################################################################################
# UNIX aliases                                                                 #
################################################################################

switch ( $MYOS )
   case Linux:
      alias view "vi -R"
      alias fastfind locate
   breaksw

   case Solaris:
      alias fastfind locate
   breaksw
endsw

# passwd alias is broken...
#alias passwd	rsh ale yppasswd

alias openscan nice +5 openscan


setenv XAPPLRESDIR	$JLOCAL/lib/app-defaults
set path = ($path $JLOCAL/scripts $JLOCAL/bin /usr/X11R6/bin)

alias hl	'set dot=$cwd ; cd /home/local/\!*'
