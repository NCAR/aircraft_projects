Summary: Control Page for AC services 
Name: raf-www-control 
Version: 1 
Release: 4
Group: Applications/Engineering
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 7.3 Linux
Requires: php php-xmlrpc php-pecl-json raf-jquery
# BuildRoot is only needed by older rpm versions
BuildRoot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
Control and status pages for ACserver

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
* Tue Aug 1 2011 <cjw@ucar.edu> 1-4
- Remove $output into xmlrpc_encode_request() in utils.php
* Thu May 31 2011 <cjw@ucar.edu> 1-3
- Support JQuery 1.5.1 and JQuery-ui 1.8.13.
* Thu Jul 8 2010 <cjw@ucar.edu> 1-2
- Fix some permissions
- Strip out xmlrpc2shell; move to ensure_running script.
- Change config.json to a config file.  This should add .rpmsave mechanism.
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
