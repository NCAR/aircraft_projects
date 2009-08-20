Summary: Configuration and plugins for nagios.
Name: raf-ac-nagios
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
# becomes RPM_BUILD_ROOT
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Requires: nagios nagios-plugins
Source: %{name}-%{version}.tar.gz

%description
Configuration and additional plugins for RAF aircraft servers.

%prep
%setup -n %{name}

%build

%pre
# localhost.cfg in fc11 will move into nagios/objects
mv $RPM_BUILD_ROOT%{_sysconfdir}/nagios/localhost.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nagios/localhost.cfg.rpmsave

%install
rm -fr $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/nagios
install -d $RPM_BUILD_ROOT/usr/lib/nagios/plugins
cp usr/lib/nagios/plugins/* $RPM_BUILD_ROOT/usr/lib/nagios/plugins

cp etc/nagios/localhost.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nagios
cp etc/nagios/raf_command.cfg $RPM_BUILD_ROOT%{_sysconfdir}/nagios

%triggerin -- nagios
# allow all access to nagios.
cf=/etc/nagios/cgi.cfg
sed -i 's/use_authentication=1/use_authentication=0/g' $cf

%post
# commands.cfg in fc11 will move into nagios/objects
cf=/etc/nagios/commands.cfg
cat /etc/nagios/raf_command.cfg >> $cf

/etc/init.d/nagios restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%config %attr(0644,root,root) %{_sysconfdir}/nagios/localhost.cfg
%config %attr(0644,root,root) %{_sysconfdir}/nagios/raf_command.cfg
%attr(0644,root,root) /usr/lib/nagios/plugins/raf_*

%changelog
* Sun Aug 23 2009 Chris Webster <cjw@ucar.edu>
- initial version
