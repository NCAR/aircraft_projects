Summary: OpenStreetMaps slippy map with OSM postGIS database and mapnik, renderd, mod_tile for rendering on demand
Name: raf-www-map
Version: 1 
Release: 1
Group: Applications/Engineering
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: mapnik mod_tile openlayers httpd php php-pgsql php-pecl-json 
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

#copy slippymap files to webspace
mkdir -p $RPM_BUILD_ROOT/var/www/html/
cp -r osm $RPM_BUILD_ROOT/var/www/html/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0664, ads, apache) /var/www/html/osm/*
%dir %attr(0775, ads, apache) /var/www/html/osm

%changelog
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
