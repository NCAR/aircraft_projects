Name: raf-ac-laptop
Version: 1
Release: 1
Summary: Package far RAF aircraft display laptops

License: GPL
BuildArch: noarch

Requires: raf-ac-chrony
Requires: raf-ac-selinux
Requires: raf-ac-gdm
Requires: firefox
Requires: xchat
Requires: tigervnc


%description
This package is a meta-package.  Its purpose is to list packages
required in the EOL computing environment, such as ntp, cups, and rsh.

%pre
# Add an ads user and ads and eol groups to system

adduser=false
addeolgroup=false
addadsgroup=false
grep -q ^ads /etc/passwd || adduser=true
grep -q ^eol /etc/group || addeolgroup=true
grep -q ^ads /etc/group || addadsgroup=true

$addeolgroup && /usr/sbin/groupadd -g 1342 -o eol
$addadsgroup && /usr/sbin/groupadd -g 1318 -o ads
$adduser && /usr/sbin/useradd  -u 12900 -N -g ads -G eol -s /bin/bash -c "ADS operator" -K PASS_MAX_DAYS=-1 ads || :

if ! grep eol /etc/group | grep -q ads; then
    usermod -G eol ads
fi


%post
chown -R ads:ads /home/ads/bin

/bin/systemctl disable firewalld
/bin/systemctl disable packagekitd


%files

%changelog
* Tue Jan 16 2017 Chris Webster <cjw@ucar.edu> 1.1
- Initial check in.

