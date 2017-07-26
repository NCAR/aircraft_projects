#
# Environment for ads user
#

# This has moved to /etc/profile.d/ads3.sh
#export AIRCRAFT=Lab_N600

export PGGRND=real-time-`echo $AIRCRAFT | cut -d _ -f 1`

#
# Get the project
#
export PROJECT=RAF_Lab
