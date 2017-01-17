Name: raf-www-map
Version: 1 
Release: 3
Summary: OpenStreetMaps slippy map with OSM postGIS database and mapnik, renderd, mod_tile for rendering on demand

License: none
Source: %{name}-%{version}.tar.gz
Distribution: RHEL 7.3 Linux
BuildArch: noarch

Requires: openlayers raf-jquery httpd php php-pgsql php-pecl-json perl perl-DBD-Pg

%description
OpenStreetMaps tile-based javascript web-viewer.

This package will install the openlayers webpage to display the tiles, using mod_tile w/ renderd to render the tiles on demand. 

%prep
%setup -q -n raf-www

# Work around for rpm thinking getCookie.pl is required rpm.
cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed -e '/perl(.::getCookie.pl)/d'
EOF
%define __perl_requires %{_builddir}/raf-www/%{name}-req
chmod 755 %{__perl_requires}


%build


%install
rm -rf $RPM_BUILD_ROOT

#copy files to webspace
mkdir -p $RPM_BUILD_ROOT/var/www/html/
cp -r flight_data $RPM_BUILD_ROOT/var/www/html/
cp flight_data/index.html $RPM_BUILD_ROOT/var/www/html/

mkdir -p $RPM_BUILD_ROOT/var/www/cgi-bin/flight_data/
mv $RPM_BUILD_ROOT/var/www/html/flight_data/cgi-bin/flight_data $RPM_BUILD_ROOT/var/www/cgi-bin/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0664, ads, apache) /var/www/html/index.html
%attr(0664, ads, apache) /var/www/html/flight_data/*html
%dir %attr(0775, ads, apache) /var/www/html/flight_data
%attr(0664, ads, apache) /var/www/html/flight_data/js/*
%dir %attr(0775, ads, apache) /var/www/html/flight_data/js
%attr(0664, ads, apache) /var/www/html/flight_data/css/*
%dir %attr(0775, ads, apache) /var/www/html/flight_data/css
%attr(0664, ads, apache) /var/www/html/flight_data/images/*
%dir %attr(0775, ads, apache) /var/www/html/flight_data/images
%attr(0664, ads, apache) /var/www/html/flight_data/GE/*
%dir %attr(0775, ads, apache) /var/www/html/flight_data/GE
%attr(0664, ads, apache) /var/www/html/flight_data/display/*
%dir %attr(0775, ads, apache) /var/www/html/flight_data/display

%attr(0775, ads, apache) /var/www/cgi-bin/flight_data/*
%dir %attr(0775, ads, apache) /var/www/cgi-bin/flight_data

%changelog
* Tue Feb 28 2012 <cjw@ucar.edu> 1-3
- Fixed image timestamp labels not being on top.
- Add 'x' to popup balloons.
- Horizontal camera display changed to 2x2 grid.
- URI updates for latest jQuery. (Spring 2011)
* Tue Jul 6 2010 <cjw@ucar.edu> 1-2
- Fixed some permissions, added top level index.html, fixed perl requires on getCookie.
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
