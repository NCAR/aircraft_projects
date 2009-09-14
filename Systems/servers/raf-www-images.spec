Summary: Images page for mission cooridinator page 
Name: raf-www-images 
Version: 1 
Release: 1
Group: Applications/Engineering
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: php jquery
Buildroot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
Images page for mission cooridinator site

%prep
%setup -n raf-www

%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/var/www/html/
cp -r images $RPM_BUILD_ROOT/var/www/html/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0664, ads, apache) /var/www/html/images/*
%dir %attr(0775, ads, apache) /var/www/html/images

%changelog
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
