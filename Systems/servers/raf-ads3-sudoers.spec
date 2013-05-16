Summary: Package containing updates for /etc/sudoers file for ADS3 data acquisition
Name: raf-ads3-sudoers
Version: 1.0
Release: 4
License: GPL
Group: System Administration
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# BuildRoot is only needed by older rpm versions
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch

Requires: sudo

%description
Package containing updates for /etc/sudoers file for ADS3 data acquisition

# %prep

# %build

# %install

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- sudo
tmpsudo=/tmp/sudoers_$$
cp /etc/sudoers $tmpsudo

# add mkfs, tune2fs, dumpe2fs to STORAGE alias
if egrep -q "^Cmnd_Alias STORAGE" $tmpsudo; then
    if ! egrep "^Cmnd_Alias STORAGE" | fgrep -q mkfs $tmpsudo; then
        sed -i -r 's@^(Cmnd_Alias STORAGE.*)$@\1, /sbin/fsck, /sbin/fsck.ext3, /sbin/mkfs, /sbin/mkfs.ext3, /sbin/tune2fs, /sbin/dumpe2fs@' $tmpsudo
    fi
else
    echo "Cmnd_Alias STORAGE = /sbin/fdisk, /sbin/sfdisk, /sbin/parted, /sbin/partprobe, /bin/mount, /bin/umount, /sbin/fsck, /sbin/fsck.ext3, /sbin/mkfs, /sbin/mkfs.ext3, /sbin/tune2fs, /sbin/dumpe2fs" >> $tmpsudo
fi

# Remove requiretty requirement for ads account so that we can
# do sudo from bootup scripts.
if egrep -q "^Defaults[[:space:]]+requiretty" $tmpsudo; then
    if ! egrep -q '^Defaults[[:space:]]*:[[:space:]]*ads[[:space:]]*!requiretty' $tmpsudo; then
        sed -i '
/^Defaults[[:space:]]*requiretty/a\
Defaults:ads !requiretty' $tmpsudo
    fi
fi

# Add /opt/nidas/bin to secure_path
if egrep -q "^Defaults[[:space:]]+secure_path" $tmpsudo; then
    if ! egrep '^Defaults[[:space:]]+secure_path' $tmpsudo | egrep -q /opt/nidas/bin; then
       sed -i -r 's,(^Defaults[[:space:]]+secure_path[[:space:]]*=[[:space:]]*[^[:space:]]+),\1:/opt/nidas/bin,' $tmpsudo
       fi
fi

if ! fgrep -q dsm_server $tmpsudo; then
cat << \EOD >> $tmpsudo
ads ALL=NOPASSWD: STORAGE,NETWORKING
ads ALL=NOPASSWD: /usr/sbin/tcpdump
ads ALL=NOPASSWD: /usr/sbin/reload_fw
ads ALL=NOPASSWD: SETENV: /opt/nidas/bin/dsm_server
EOD
fi

if fgrep -q /opt/local/nidas/x86 $tmpsudo; then
    sed -i s,/opt/local/nidas/x86,/opt/nidas,g $tmpsudo
fi

visudo -c -f $tmpsudo && cp $tmpsudo /etc/sudoers
rm -f $tmpsudo

%post
# if ! chkconfig --list ads3 > /dev/null 2>&1; then
#     echo "ads3 service is not setup to run at boot"
#     chkconfig --list ads3
# fi

# provide write access to /opt/ael-dpkgs
if egrep -q "^ads" /etc/passwd; then
    chown -R ads /opt/ael-dpkgs
fi
if egrep -q "^eol" /etc/group; then
    chgrp -R eol /opt/ael-dpkgs
    chmod -R g+sw /opt/ael-dpkgs
fi

%files

%changelog
* Thu May 16 2013 Chris Webster <cjw@ucar.edu> 1.0-4
- Add firewire driver reload program (reload_fw) for cameras.
* Thu Apr  7 2012 Gordon Maclean <maclean@ucar.edu> 1.0-3
- Updates for moves of nidas and ael-dpkgs from /opt/local to /opt.
* Thu Mar 18 2010 Gordon Maclean <maclean@ucar.edu> 1.0-2
- sed -ir should be sed -i -r
* Fri Nov 6 2009 Gordon Maclean <maclean@ucar.edu> 1.0-1
- initial
