Summary: Control Page for AC services 
Name: raf-www-control 
Version: 1 
Release: 2
Group: Applications/Engineering
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: php php-pecl-json jquery
# BuildRoot is only needed by older rpm versions
BuildRoot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
Controls page for ACserver

%prep
%setup -n raf-www

%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/var/www/html/
cp -r control $RPM_BUILD_ROOT/var/www/html/

%post

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,ads,apache)
/var/www/html/control
%config /var/www/html/control/js/config.json

%changelog
* Thu Jul 8 2010 <cjw@ucar.edu> 1-2
- Fix some permissions
- Strip out xmlrpc2shell; move to ensure_running script.
- Change config.json to a config file.  This should add .rpmsave mechanism.
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
