#!/bin/csh

if ($#argv != 2) then
  echo "This script is intended to set project specific variables"	
  echo "on a per computer basis, so full init_project doesn't have"	
  echo "to be run on groundstation + acserver + networked servers."	
  echo "Simplifies workflow a bit."

  echo "Usage:"
  echo "init_project ProjectName {Platform}"
  echo
  echo "The optional Platform argument puts the script into non-interactive"
  echo "mode"
  echo
  echo -n "Proceed (y/N) ? "
  set proceed = $<

  if ($proceed != "y") then
    exit(1)
  endif

  if ($#argv == 0) then
    echo "Usage:\n init_project ProjectName {Platform}\n"
    exit(0)
  endif

  echo "\nChoose platform:"
  echo "  1. NCAR C130"
  echo "  2. NCAR GV"
  echo "  3. Lab system"
  echo -n "Enter (1-3) ? "
  set platform = $<

  switch ($platform)
    case [1]:
      set platform = 'C130_N130AR'
      breaksw
    case [2]:
      set platform = 'GV_N677F'
      breaksw
    case [3]:
      set platform = 'Lab_N600'
      set proj = 'RAF_Lab'
      breaksw
    default:
      echo "Invalid choice."
      exit(0)
  endsw
else
  set platform=$argv[2]
endif

if ("$proj" != "RAF_Lab") then
  set proj=$argv[1]
endif

/bin/mkdir -vp -m g+s $RAW_DATA_DIR/$proj/
/bin/mkdir -vp -m g+s $DATA_DIR/$proj

echo "\nSetting group write permissions."
/bin/chmod -vR g+w,o-w $PROJ_DIR/$proj $RAW_DATA_DIR/$proj $DATA_DIR/$proj
/bin/chgrp -vR proj $PROJ_DIR/$proj $RAW_DATA_DIR/$proj $DATA_DIR/$proj


echo "\nSetting project"
/usr/bin/sed -i 's/^export PROJECT=.*/export PROJECT='"$proj"'/' ~/ads3_environment.sh

echo "\nSetting aircraft"
if ( -e "/etc/sysconfig/aircraft" ) then
    echo " in /etc/sysconfig/aircraft as another user"
    su root -c "/usr/bin/sed -i 's/^AIRCRAFT=.*/AIRCRAFT='"$platform"'/' /etc/sysconfig/aircraft"
else
    echo " in ads3_environment.sh"
    /usr/bin/sed -i 's/^#export AIRCRAFT=.*/export AIRCRAFT='"$platform"'/' ~/ads3_environment.sh
    /usr/bin/sed -i 's/^export AIRCRAFT=.*/export AIRCRAFT='"$platform"'/' ~/ads3_environment.sh
endif


echo "Logout of current user or reboot to see these applied"
