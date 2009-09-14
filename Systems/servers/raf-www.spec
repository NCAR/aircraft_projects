Summary: Display page, and all content
Name: raf-www
Version: 1
Release: 1
Group: Applications/Web
License: none
Distribution: RHEL 5.3 Linux
Requires: raf-www-camera raf-www-control raf-www-images raf-www-map raf-www-index 
Buildroot: %{_tmppath}/%{name}-root
BuildArch: noarch

%description
This is a meta-package which installs all of the MC site pages. 

%prep

%build

%install
rm -rf $RPM_BUILD_ROOT

%files

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Sep 14 2009 <dlagreca@ucar.edu> 1-1
- created initial package
