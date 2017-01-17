Name: raf-ac-nfs
Version: 1
Release: 2
Summary: Setup default NFS exports

License: GPL
Packager: Chris Webster <cjw@ucar.edu>
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

%if 0%{?rhel} >= 7
/bin/systemctl enable nfs
%else
/sbin/chkconfig --levels 345 nfs on
%endif


%files
%defattr(-,ads,ads)
%dir %attr(0775,ads,ads) /mnt/r1/camera_images

%changelog
* Mon Jan 16 2017 Chris Webster <cjw@ucar.edu> - 1.0-2
- Add systemectl for RH7.
* Fri Aug 5 2011 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
