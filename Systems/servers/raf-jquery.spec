Name: raf-jquery 
Version: 1.5.1 
Release: 2
Summary: jQuery js library

License: GPL 
Source: %{name}-%{version}.tar.gz
Distribution: RHEL 7.3 Linux
BuildArch: noarch
Requires: httpd

%description

This package will install the jquery library

To get custom zip file:  Goto jquery-ui.com/download and build the custom .zip file.
Choose smoothess Theme on the rioght bar and then hit the Dowload button.

Don't forget to update raf-www-camera and raf-www-control index.html files to load
latest jQuery files from /usr/lib

%prep
%setup -q -n %{name}

%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/etc/httpd/conf.d/
mkdir -p $RPM_BUILD_ROOT%_libdir/jQuery
# unzip $RPM_SOURCE_DIR/jquery-ui-1.8.13.custom.zip  -d $RPM_BUILD_ROOT%_libdir/jQuery/

cp -r usr/lib/jQuery ${RPM_BUILD_ROOT}%_libdir

conf=$RPM_BUILD_ROOT/etc/httpd/conf.d/jQuery.conf
echo "Alias /jQuery %_libdir/jQuery" > $conf
echo "<Directory %_libdir/jQuery>" >> $conf
echo -e "\tOptions None" >> $conf
echo -e "\tRequire all granted" >> $conf
echo "</Directory>" >> $conf

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,ads,ads)
%dir %attr(0775, ads,ads) %_libdir/jQuery
%_libdir/jQuery/*
%config /etc/httpd/conf.d/jQuery.conf

%changelog
* Wed Feb  8 2017 <cjw@ucar.edu>
- Apache 2.4 requires a 'Require all granted' for all conf.d files.
* Tue Jan 24 2017 <cdewerd@ucar.edu>
- Added require httpd, source as a tar
* Sat Dec  3 2016 <cjw@ucar.edu>
- Rename from jquery to raf-jquery...notloading under CentOS7.
* Tue May 17 2011 <cjw@ucar.edu>
- update for jquery 1.5.1 and jqueryui 1.8.13
* Wed Aug 26 2009 <dlagreca@ucar.edu> 2.8-1
- created initial package 
