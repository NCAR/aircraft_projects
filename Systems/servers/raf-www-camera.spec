Summary: Web-based live camera image viewer (for use with capture program)
Name: raf-www-camera
Version: 1
Release: 1
Group: Applications/Web
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: httpd php php-pgsql php-pecl-json jquery
Buildroot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
	This is the front-end viewer package that works with the ieee1394 capture program, and capture-camserver backend. This package will install files necissary for the website into /var/www/html/camera and should be accessable at http://localhost/camera.

%prep
%setup -n raf-www

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/var/www/html
cp -r camera $RPM_BUILD_ROOT/var/www/html/

%post
mkdir /mnt/r2/camera_images
ln -s /mnt/r2/camera_images /var/www/html/camera/camera_images
phpconf=`find /etc -name "php.conf"`
echo "SetEnv PGHOST acserver" >> $phpconf
echo "SetEnv PGUSER ads" >> $phpconf
echo "SetEnv PGDATABASE real-time" >> $phpconf
service httpd restart

%postun
rm /var/www/html/camera/camera_images
phpconf=`find /etc -name "php.conf"`
sed -i '/SetEnv PGHOST/ d' $phpconf
sed -i '/SetEnv PGUSER/ d' $phpconf
sed -i '/SetEnv PGDATABASE/ d' $phpconf
service httpd restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0664,ads,apache)
%dir %attr(0775,ads,apache) /var/www/html/camera
%dir %attr(0775,ads,apache) /var/www/html/camera/css
%dir %attr(0775,ads,apache) /var/www/html/camera/js
/var/www/html/camera/*

%changelog
* Mon Aug 31 2009 <dlagreca@ucar.edu> 0.1-1
- detached jquery library from this package, now requires raf-jquery

* Wed Jul 22 2009 <dlagreca@ucar.edu> 0.1-1
- set correct permissions on /var/www/html/camera/css/smoothness/images

* Tue Jul 1 2009 <dlagreca@ucar.edu> 0.1-1
- created initial package
