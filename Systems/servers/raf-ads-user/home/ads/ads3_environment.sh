#
# Environment for ads user
#

export AIRCRAFT=Lab_N600
#export AIRCRAFT=GV_N677F
#export AIRCRAFT=C130_N130AR

export PGGRND=real-time-`echo $AIRCRAFT | cut -d _ -f 1`

#
# Get the project
#
export PROJECT=RAF_Lab
