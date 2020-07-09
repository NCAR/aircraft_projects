#!/bin/sh

alias echo="echo -e"

function usage
{
  echo "\nPlease specify board type and DSM."
  echo "\nExample:"
  echo "\t$0 dsm319 viper [rsync|kernel]"
  echo "\t$0 dsmRWO vulcan [rsync|kernel]"
  echo
  echo "You will need a console port actively connected to the DSM!"
  echo
  echo "This script should be run thrice.  When using this script"
  echo "the 'rsync' option should be used first to install rsync."
  echo
  echo "Then use the 'kernel' option.  The DSM will be automatically"
  echo "rebooted.  Press Ctrl-C to drop into RedBoot to set up"
  echo "its kernel as such..."
  echo "\nfor VIPER:"
  echo "\tRedBoot> alias kernel"
  echo "\t'kernel' = '/boot/vmlinuz-2.6.16.28-arcom1-1-viper'"
  echo "\tRedBoot> alias kernel /boot/vmlinuz-2.6.16.28-arcom1-2-viper"
  echo "\tRedBoot> reset"
  echo "\nfor VULCAN:"
  echo "\tRedBoot> alias kernel"
  echo "\t'kernel' = '/boot/vmlinuz-2.6.11.11-arcom1-2-vulcan'"
  echo "\tRedBoot> alias kernel /boot/vmlinuz-2.6.21.7-ael1-2-vulcan"
  echo "\tRedBoot> reset"
  echo
}

if [ $# -lt 2 ]; then
  usage
  exit
fi

case $2 in
viper) be="";;
vulcan) be="be";;
*)
  usage; exit;;
esac

echo "'$1' uses an arm$be processor.\n"

# Test to see if the DSM is on-line.
#
ping -c 1 -W 2 $1 > /dev/null || exit $?

# You will be confronted with the following issue regarding
# the RSA key:
#
# The authenticity of host '192.168.184.1 (192.168.184.1)' can't be established.
# RSA key fingerprint is 7d:3f:25:86:4e:26:9c:30:f4:13:67:4d:72:41:3e:dc.
# Are you sure you want to continue connecting (yes/no)? yes
# Warning: Permanently added '192.168.184.1' (RSA) to the list of known hosts.
# ads@192.168.184.1's password: 
#
if [ $# == 3 ] && [ $3 == "rsync" ] ; then
  echo "Shelling into '$1'... Issue the following commands then type 'exit' to resume."
  echo
  echo "scp ads@192.168.184.1:/opt/local/ael-dpkgs/ads3/root-user_*_all.deb /tmp/"
  echo "dpkg -i -F depends /tmp/root-user_*_all.deb"
  echo "scp ads@192.168.184.1:/opt/local/ael-dpkgs/rsync_*_arm$be.deb /tmp/"
  echo "dpkg -i -F depends /tmp/rsync_*_arm$be.deb"
  echo
  ssh root@$1
  echo "\n\t...now run '$0 $1 $2 kernel' to install the latest kernel.\n"
  exit
fi

# You still need console access to the DSM in order to install the latest
# kernel.  After this reboots Ctrl-C the console to drop into RedBoot.
#
if [ $# == 3 ] && [ $3 == "kernel" ] ; then
  echo "\n\tInstalling the kernel... watch for the reboot in the serial console!"
  echo "\nClick on the terminal and get ready to press Ctrl-C to drop into RedBoot"
  echo "over there.  If you miss it the DSM will still boot with its older kernel."
  echo "Simply log in over there, reboot and try again."
  echo "\n\twatch for the 'Trying NPE-B...success. Using NPE-B with PHY 0.'"

  case $2 in
  viper)
    echo "\nfor VIPER:"
    echo "\tRedBoot> alias kernel"
    echo "\t'kernel' = '/boot/vmlinuz-2.6.16.28-arcom1-1-viper'"
    echo "\tRedBoot> alias kernel /boot/vmlinuz-2.6.16.28-arcom1-2-viper"
    echo "\tRedBoot> reset"
    ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/linux-image-2.6.16.28-arcom1-2-viper_ncar.2_arm.deb /tmp/"
    ssh root@$1 "dpkg -i -F depends /tmp/linux-image-2.6.16.28-arcom1-2-viper_ncar.2_arm.deb"
    ;;
  vulcan)
    echo "\nfor VULCAN:"
    echo "\tRedBoot> alias kernel"
    echo "\t'kernel' = '/boot/vmlinuz-2.6.11.11-arcom1-2-vulcan'"
    echo "\tRedBoot> alias kernel /boot/vmlinuz-2.6.21.7-ael1-2-vulcan"
    echo "\tRedBoot> reset"
    ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/linux-image-2.6.21.7-ael1-2-vulcan_ncar.1_armbe.deb /tmp/"
    ssh root@$1 "dpkg -i -F depends /tmp/linux-image-2.6.21.7-ael1-2-vulcan_ncar.1_armbe.deb"
    ;;
  esac
  echo "\nRebooting the DSM."
  ssh root@$1 "reboot"
  echo "\n\t...now run '$0 $1 $2' After the DSM finishes booting.\n"
  exit
fi

# The remainder of the script will operate w/o need of user intervention...
#
ssh root@$1 uname -a

ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/isfs/libelf0_*_arm$be.deb /tmp/"
ssh root@$1 "dpkg -i -F depends /tmp/libelf0_*_arm$be.deb"
ssh root@$1 "ls -lrt /tmp/*.deb"
ssh root@$1 "rm /tmp/*.deb"

ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/*_arm$be.deb /tmp/"
ssh root@$1 "dpkg -i -F depends /tmp/gawk_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/libxerces-c_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/libxmlrpc++_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/minicom_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/ntpd_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/ntpdate_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/procps_*_arm$be.deb"
ssh root@$1 "ls -lrt /tmp/*.deb"
ssh root@$1 "rm /tmp/*.deb"

ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/ads3/etc-files_*_all.deb /tmp/"
ssh root@$1 "dpkg -i -F depends /tmp/etc-files_*_all.deb"
ssh root@$1 "ls -lrt /tmp/*.deb"
ssh root@$1 "rm /tmp/*.deb"

# Give the DSM its name.
#
rm -f /tmp/$0-hostname
cat > /tmp/$0-hostname << EOF_HOSTNAME
$1
EOF_HOSTNAME
scp /tmp/$0-hostname root@$1:/etc/hostname
rm -f /tmp/$0-hostname

# Check to see of the CF card is ready.
#
ssh root@$1 "umount /media/cf"
ssh root@$1 "mount /media/cf"
if [ `ssh root@$1 "df | grep -c hda1"` -eq 0 ]; then
  echo "CF not set up or present on '$1'"
  exit
fi

# Purge what was once on the CF card.
#
ssh root@$1 "rm -rf /media/cf/*"

# These debian packages get installed on the CF card.
#
ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/ads3/*_all.deb /tmp/"
ssh root@$1 "dpkg -i -F depends /tmp/ads3-firmware_*_all.deb"
ssh root@$1 "ls -lrt /tmp/*.deb"
ssh root@$1 "rm /tmp/*.deb"

ssh root@$1 "rsync rsync://192.168.184.1/ael-dpkgs/ads3/*_arm$be.deb /tmp/"
ssh root@$1 "dpkg -i -F depends /tmp/ads3-modules_*_arm$be.deb"
ssh root@$1 "dpkg -i -F depends /tmp/pcmcom8_*_arm$be.deb"
ssh root@$1 "ls -lrt /tmp/*.deb"
ssh root@$1 "rm /tmp/*.deb"

ssh root@$1 "depmod" 

echo "\n\tRebooting the DSM... This script will resume processing in 2 minutes.\n"; date
ssh root@$1 "reboot"
sleep 120
ping -c 1 -W 2 $1 > /dev/null || exit $?

echo "__________________________________"
echo "does the DSM know was time it is? \\____________________"
ssh root@$1 "date"
echo "_______________________"
echo "are the modues loaded? \\_______________________________"
ssh root@$1 "lsmod"
echo "____________________"
echo "is the dsm running? \\__________________________________"
ssh root@$1 "ps aux | grep dsm"
echo "___________________________________"
echo "is the compact flash card mounted? \\___________________"
ssh root@$1 "df"
echo "\n\n"
