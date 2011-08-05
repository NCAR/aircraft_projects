Summary: Setup default NFS exports
Name: raf-ac-nfs
Version: 1
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
BuildRoot: %{_tmppath}/%{name}-root
Vendor: UCAR
BuildArch: noarch
Requires: nfs-utils

%description

%prep

%build

%install
mkdir -p ${RPM_BUILD_ROOT}/mnt/r1/camera_images

%post

echo "/mnt/r1 192.168.0.0/16(rw,sync,root_squash,anonuid=12900,anongid=1318)" >> /etc/exports

/usr/sbin/exportfs -a
/sbin/chkconfig --levels 345 nfs on


%files
%defattr(-,ads,ads)
/mnt/r1/camera_images

%changelog
* Fri Aug 5 2011 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
