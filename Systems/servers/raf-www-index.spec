Summary: Display page (navigaion buttons above iframe for content)
Name: raf-www-index
Version: 1
Release: 1
Group: Applications/Web
Source: %{name}-%{version}.tar.gz
License: none
Distribution: RHEL 5.3 Linux
Requires: jquery
Buildroot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
This package installs the index page for MC site (buttons across the top, content below). 

%prep
%setup -n raf-www

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/var/www/html/
cp index.html $RPM_BUILD_ROOT/var/www/html/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0664,ads,apache)
/var/www/html/index.html

%changelog
* Mon Aug 31 2009 <dlagreca@ucar.edu> 1-1
- created initial package
