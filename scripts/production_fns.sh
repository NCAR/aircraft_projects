#!/bin/bash

SCR_DIR=/scr/tmp/nimbus
SAVE_DIR=`pwd`

initialize_processing()
{
mkdir -p ${DAT}

if [ `whoami` == nimbus ]; then
  clone_production
fi
}

cleanup_processing()
{
if [ `whoami` == nimbus ]; then
  cleanup_production
fi
}


# Reorder netCDF files in the $DAT directory.
#
reorder_all() {

busyFile='reorderInProgress'
trap "rm $busyFile" SIGINT SIGTERM

cd ${DAT}

if [ -f $busyFile ]; then
  exit 1
fi

touch $busyFile

for file in ${PROJ}?f??.nc
do
  echo $file
  ncdump -h $file | head | grep --quiet UNLIMITED
  if [ $? -eq 0 ]; then
    nccopy -u $file reotemp.nc
    mv -f reotemp.nc $file
    chmod g+w $file
  fi
done

/bin/rm $busyFile
cd $SAVE_DIR
}


# Kalman Filter script.
#
run_kalmanFilter() {

cd ~nimbus/RStudio/KalmanFilter

# To apply the corrections to a high-rate file, supply the flight with an h
#  e.g.  Rscript KalmanFilter.R WCR-TEST tf01h y y n 15
for file in ${DAT}/${PROJ}[rtf]f??.nc
do
  flight=`echo $file | awk '{print substr($0,length($0)-6,4)}'`
  Rscript KalmanFilter.R $PROJ $flight y y n 15
done

cd $SAVE_DIR
}


clone_production() {

  cd ${SCR_DIR}
  
  git clone --recursive git@github.com:NCAR/nimbus.git
  cd nimbus
  scons
  retval=$?
  if [ $retval -ne 0 ]; then
    exit $retval
  fi
  export PATH=${SCR_DIR}/nimbus/src/filter:$PATH

  SAVE_PROJ_DIR=$PROJ_DIR
  export PROJ_DIR=${SCR_DIR}/projects
  git clone git@github.com:NCAR/aircraft_projects.git ${PROJ_DIR}
  cd ${PROJ_DIR}/${PROJ}/${AIRCRAFT}/Production
}

cleanup_production() {

  /bin/cp logfile* ${SAVE_PROJ_DIR}/${PROJ}/${AIRCRAFT}/Production
  cd
  rm -rf ${PROJ_DIR} ${SCR_DIR}/nimbus
  export PROJ_DIR=$SAVE_PROJ_DIR
}
