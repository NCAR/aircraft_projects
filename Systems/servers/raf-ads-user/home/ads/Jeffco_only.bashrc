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

export LOCAL=/opt/local
export JLOCAL=/opt/local

# next 3 lines moved from System.cshrc on 24Feb04 - SN
export PRINTER=raf-hp2300
export LPDEST=raf-hp2300

if [ -z "$PROJ_DIR" ]; then
   export PROJ_DIR=/home/local/projects
fi

if [ -z "$RAW_DATA_DIR" ]; then
   export RAW_DATA_DIR=/var/r1/
fi

if [ -z "$DATA_DIR" ]; then
   export DATA_DIR=/home/data
fi

################################################################################
# 3rd party software environment variables                                     #
################################################################################

# University Hawaii GMT package, used by ncplot geo-pol map.
export GMT_SHAREDIR=/usr/share/GMT

export XAPPLRESDIR=/usr/share/X11/app-defaults


################################################################################
# UNIX aliases                                                                 #
################################################################################

alias view="vi -R"

export PATH=$PATH:$JLOCAL/scripts

alias hl='set dot=$cwd ; cd /home/local/\!*'
alias ninc='set dot=$cwd ; cd /home/local/raf/nimbus/include/\!*'
alias nsrc='set dot=$cwd ; cd /home/local/raf/nimbus/src/\!*'
