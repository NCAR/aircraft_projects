Name: raf-www-map
Version: 1 
Release: 4
Summary: Web packages

License: none
Source: %{name}-%{version}.tar.gz
Distribution: RHEL 7.3 Linux
BuildArch: noarch

Requires: raf-ads-user
Requires: raf-jquery httpd php php-pgsql php-pecl-json perl perl-DBD-Pg

%description
Install web sub-packages for controls/, cameras/, and maps artwork pages.


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
(cd $RPM_BUILD_ROOT/var/www/html/flight_data/display; tar xf windbarbs.tar.gz; rm windbarbs.tar.gz)

mkdir -p $RPM_BUILD_ROOT/var/www/cgi-bin/flight_data/
mv $RPM_BUILD_ROOT/var/www/html/flight_data/cgi-bin/flight_data $RPM_BUILD_ROOT/var/www/cgi-bin/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0664, ads, apache, 0775)
/var/www/html/index.html
/var/www/html/flight_data
/var/www/cgi-bin/flight_data

%changelog
* Thu Feb 22 2018 <cjw@ucar.edu> 1-4
- Cleanup Requires and Comments, since cno longer does openlayers / OSM.
- tar up wind-barbs in svn and un tar in this package install.
* Fri Aug 4 2017 <cjw@ucar.edu> 1-3
- Cleanup %files section of spec file.
* Tue Feb 28 2012 <cjw@ucar.edu> 1-3
- Fixed image timestamp labels not being on top.
- Add 'x' to popup balloons.
- Horizontal camera display changed to 2x2 grid.
- URI updates for latest jQuery. (Spring 2011)
* Tue Jul 6 2010 <cjw@ucar.edu> 1-2
- Fixed some permissions, added top level index.html, fixed perl requires on getCookie.
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
