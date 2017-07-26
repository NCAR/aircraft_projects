Name: raf-ac-laptop
Version: 1
Release: 3
Summary: Package far RAF aircraft display laptops

License: GPL
Source: %{name}-%{version}.tar.gz
BuildArch: noarch

Requires: raf-ac-chrony
Requires: raf-ac-selinux
Requires: raf-ac-gdm
Requires: firefox
Requires: xchat
Requires: tigervnc
# Adding this so we can build aeros locally...
Requires: raf-devel


%description
This package is a meta-package.  Its purpose is to list packages
required in the EOL computing environment, such as ntp, cups, and rsh.

%prep
%setup -q -n %{name}


%pre

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


%build

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}/home/ads

/bin/cp -r home/ads/.ssh                  ${RPM_BUILD_ROOT}/home/ads


%post
/bin/systemctl disable firewalld
/bin/systemctl disable packagekitd

/bin/rm /etc/localtime
/bin/ln -s /usr/share/zoneinfo/UTC /etc/localtime


%files
%defattr(-,ads,ads)
%attr(0700,ads,ads) /home/ads/.ssh
%attr(0600,ads,ads) /home/ads/.ssh/authorized_keys


%changelog
* Wed Jul 26 2017 Chris Webster <cjw@ucar.edu> 1.3
- Add .ssh/authorized_key populated with id_rsa.pub
- Removed /home/ads/bin.  Not needed at the moment.
* Tue Jul 25 2017 Chris Webster <cjw@ucar.edu> 1.2
- Add raf-devel
- Set timezone.
* Mon Jan 16 2017 Chris Webster <cjw@ucar.edu> 1.1
- Initial check in.

