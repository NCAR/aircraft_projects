Summary: Control Page for AC services 
Name: raf-www-control 
Version: 1 
Release: 1
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
#add to sessions config
ASFILE = ~/.config/autostart/python.desktop
rm $ASFILE
touch $ASFILE

echo "[Desktop Entry]" >>$ASFILE
echo "Name=No name" >>$ASFILE
echo "Encoding=UTF-8" >>$ASFILE
echo "Version=1.0" >>$ASFILE
echo "Exec=/usr/bin/python /home/local/Systems/scripts/xmlrpc2shell.py" >>$ASFILE
echo "X-GNOME-Autostart-enabled=true" >>$ASFILE

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%dir %attr(0775, ads, apache) /var/www/html/control
%dir %attr(0775, ads, apache) /var/www/html/control/js
%dir %attr(0775, ads, apache) /var/www/html/control/css
%attr(0664, ads, apache) /var/www/html/control/*

%changelog
* Fri Sep 4 2009 <dlagreca@ucar.edu> 1-1
- created initial package 
