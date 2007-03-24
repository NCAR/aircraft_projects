#
# Info on ntpd package for viper
# 
# The ntpd package distributed with AEL just contains the ntpd
# executable. We want ntpq and a few others, and want
# linuxpps support.

# PPS website
http://wiki.enneenne.com/index.php/LinuxPPS_support

# Get timepps.h from kernel patch, copy it to the cross-compiler 
# include directory.

cp include/linux/timepps.h /opt/arcom/arm-linux/include

