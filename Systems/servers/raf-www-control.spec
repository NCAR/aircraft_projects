Summary: Control Page for AC services 
Name: raf-www-control 
Version: 1 
Release: 1
Group: Applications/Engineering
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: php php-pgsql php-pecl-json jquery
Buildroot: %{_tmppath}/%{name}-root
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

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0664, ads, apache) /var/www/html/control/*
%dir %attr(0775, ads, apache) /var/www/html/control

%changelog
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
