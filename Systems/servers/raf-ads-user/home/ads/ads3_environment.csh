#
# Environment for ads user
#

# This has moved to /etc/profile.d/ads3.csh
#setenv AIRCRAFT Lab_N600

setenv PGGRND real-time-`echo $AIRCRAFT | cut -d _ -f 1`

#
# Get the project
#
setenv PROJECT RAF_Lab
