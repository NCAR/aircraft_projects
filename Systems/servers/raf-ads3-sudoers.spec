Summary: Package containing updates for /etc/sudoers file for ADS3 data acquisition
Name: raf-ads3-sudoers
Version: 1.0
Release: 1
License: GPL
Group: System Administration
BuildArch: noarch
BuildRoot: /tmp/%{name}-%{version}
Source: %{name}-%{version}.tar.gz

Requires: sudo

%description
Package containing updates for /etc/sudoers file for ADS3 data acquisition

%prep

%build

%install

%triggerin -- sudo
tmpsudo=/tmp/sudoers_$$
cp /etc/sudoers $tmpsudo

# add mkfs, tune2fs, dumpe2fs to STORAGE alias
if egrep -q "^Cmnd_Alias STORAGE" $tmpsudo; then
    if ! egrep "^Cmnd_Alias STORAGE" | fgrep -q mkfs $tmpsudo; then
        sed -ir 's@^(Cmnd_Alias STORAGE.*)$@\1, /sbin/fsck, /sbin/fsck.ext3, /sbin/mkfs, /sbin/mkfs.ext3, /sbin/tune2fs, /sbin/dumpe2fs@' $tmpsudo
    fi
else
    echo "Cmnd_Alias STORAGE = /sbin/fdisk, /sbin/sfdisk, /sbin/parted, /sbin/partprobe, /bin/mount, /bin/umount, /sbin/fsck, /sbin/fsck.ext3, /sbin/mkfs, /sbin/mkfs.ext3, /sbin/tune2fs, /sbin/dumpe2fs" >> $tmpsudo
fi

# Remove requiretty requirement for ads account so that we can
# do sudo from bootup scripts.
if egrep -q "^Defaults[[:space:]]+requiretty" $tmpsudo; then
    if ! egrep -q '^Defaults[[:space:]]*:[[:space:]]*ads[[:space:]]*!requiretty/' $tmpsudo; then
        sed -ire '
/^Defaults[[:space:]]*requiretty/a\
Defaults:ads !requiretty' $tmpsudo
    fi
fi

if ! fgrep -q dsm_server $tmpsudo; then
cat << \EOD >> $tmpsudo
ads ALL=NOPASSWD: STORAGE,NETWORKING
ads ALL=NOPASSWD: /usr/sbin/tcpdump
ads ALL=NOPASSWD: SETENV: /opt/local/nidas/x86/bin/dsm_server
EOD
fi

visudo -c -f $tmpsudo && cp $tmpsudo /etc/sudoers
rm -f $tmpsudo

%post
# if ! chkconfig --list ads3 > /dev/null 2>&1; then
#     echo "ads3 service is not setup to run at boot"
#     chkconfig --list ads3
# fi

# provide write access to /opt/local/ael-dpkgs
if egrep -q "^ads" /etc/passwd; then
    chown -R ads /opt/local/ael-dpkgs
fi
if egrep -q "^eol" /etc/group; then
    chgrp -R eol /opt/local/ael-dpkgs
    chmod -R g+sw /opt/local/ael-dpkgs
fi

%files

%changelog
* Fri Nov 6 2009 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial
