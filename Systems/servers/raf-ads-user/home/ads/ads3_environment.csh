#
# Environment for ads user
#

setenv AIRCRAFT Lab_N600
#setenv AIRCRAFT GV_N677F
#setenv AIRCRAFT C130_N130AR

setenv PGGRND real-time-`echo $AIRCRAFT | cut -d _ -f 1`

#
# Get the project
#
setenv PROJECT RAF_Lab
