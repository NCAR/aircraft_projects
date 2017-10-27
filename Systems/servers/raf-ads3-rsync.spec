Name: raf-ads3-rsync
Version: 1.0
Release: 1
Summary: Additions to rsync config.

License: GPL
Source: %{name}-%{version}.tar.gz
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: rsync

%description
Additions to rsync config to allow dsms and instruments to rsync in.

%prep
%setup -q -n %{name}

%build

%install
rm -fr $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/%{_sysconfdir}
cp -r etc/* $RPM_BUILD_ROOT/%{_sysconfdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
systemctl enable rsyncd.service
systemctl start rsyncd.service


%files
%defattr(-,root,root)
%config %attr(0755,root,root) /etc/rsyncd.conf

%changelog
* Fri Oct 27 2017 Chris Webster <cjw@ucar.edu>
- initial version.
