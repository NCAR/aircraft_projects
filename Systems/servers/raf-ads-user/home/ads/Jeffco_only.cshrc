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


setenv LOCAL /opt/local

# next 3 lines moved from System.cshrc on 24Feb04 - SN
setenv PRINTER               raf-hp2300
setenv LPDEST                raf-hp2300

setenv JLOCAL /opt/local

if (!($?PROJ_DIR)) then
   setenv PROJ_DIR /home/local/projects
endif

if (!($?RAW_DATA_DIR)) then
   setenv RAW_DATA_DIR /var/r1/
endif

if (!($?DATA_DIR)) then
   setenv DATA_DIR /home/data
endif

if (!($?PROD_DATA)) then
   setenv PROD_DATA /scr/productiondata
endif

################################################################################
# 3rd party software environment variables                                     #
################################################################################

# University Hawaii GMT package, used by ncplot geo-pol map.

setenv GMTHOME		$LOCAL/GMT

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

setenv XAPPLRESDIR	/usr/share/X11/app-defaults

set path = ($path $JLOCAL/scripts $JLOCAL/bin /usr/X11R6/bin)

alias hl	'set dot=$cwd ; cd /home/local/\!*'
alias ninc      'set dot=$cwd ; cd /home/local/raf/nimbus/include/\!*'
alias nsrc      'set dot=$cwd ; cd /home/local/raf/nimbus/src/\!*'
