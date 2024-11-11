#!/bin/bash

SCR_DIR=/scr/tmp/nimbus

clone_production() {

  cd ${SCR_DIR}
  
  git clone --recursive https://github.com/NCAR/nimbus
  cd nimbus
  scons
  retval=$?
  if [ $retval -ne 0 ]; then
    exit $retval
  fi
  export PATH=${SCR_DIR}/nimbus/src/filter:$PATH

  SAVE_PROJ_DIR=$PROJ_DIR
  export PROJ_DIR=${SCR_DIR}/projects
  git clone https://github.com/NCAR/aircraft_projects.git ${PROJ_DIR}
  cd ${PROJ_DIR}/${PROJ}/${AIRCRAFT}/Production
}

cleanup_production() {
  /bin/cp logfile* ${SAVE_PROJ_DIR}/${PROJ}/${AIRCRAFT}/Production
  cd
  rm -rf ${PROJ_DIR} ${SCR_DIR}/nimbus
  export PROJ_DIR=$SAVE_PROJ_DIR
}
