Summary: OpenStreetMaps slippy map with OSM postGIS database and mapnik, renderd, mod_tile for rendering on demand
Name: raf-www-map
Version: 1 
Release: 1
Group: Applications/Engineering
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: openlayers jquery httpd php php-pgsql php-pecl-json 
Buildroot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
OpenStreetMaps tile-based javascript web-viewer.

This package will install the openlayers webpage to display the tiles, using mod_tile w/ renderd to render the tiles on demand. 

%prep
%setup -n raf-www

%build


%install
rm -rf $RPM_BUILD_ROOT

#copy files to webspace
mkdir -p $RPM_BUILD_ROOT/var/www/html/
cp -r flight_data $RPM_BUILD_ROOT/var/www/html/

mkdir -p $RPM_BUILD_ROOT/var/www/cgi-bin/flight_data/
mv $RPM_BUILD_ROOT/var/www/html/flight_data/cgi-bin/flight_data $RPM_BUILD_ROOT/var/www/cgi-bin/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0664, ads, apache) /var/www/html/flight_data/*
%dir %attr(0775, ads, apache) /var/www/html/flight_data

%attr(0664, ads, apache) /var/www/cgi-bin/flight_data/*
%dir %attr(0775, ads, apache) /var/www/cgi-bin/flight_data

%changelog
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
