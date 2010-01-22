Summary: Configuration and plugins for nagios
Name: raf-ac-nagios
Version: 1.0
Release: 2
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

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_sysconfdir}/nagios
install -d %{buildroot}%{_libdir}/nagios/plugins
cp usr/lib/nagios/plugins/* %{buildroot}%{_libdir}/nagios/plugins

cp etc/nagios/raf_commands.cfg %{buildroot}%{_sysconfdir}/nagios
cp etc/nagios/raf_localhost.cfg %{buildroot}%{_sysconfdir}/nagios

%triggerin -- nagios
# allow all access to nagios.
cf=/etc/nagios/cgi.cfg
sed -i 's/use_authentication=1/use_authentication=0/g' $cf

%post
# commands.cfg in fc11 will move into nagios/objects
cf=/etc/nagios/nagios.cfg
sed -i 's/commands.cfg/commands.cfg\n\ncfg_file=\/etc\/nagios\/raf_commands.cfg/' $cf
sed -i 's/\/localhost.cfg/\/raf_localhost.cfg/' $cf

/etc/init.d/nagios restart

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_sysconfdir}/nagios/raf_commands.cfg
%{_sysconfdir}/nagios/raf_localhost.cfg
%{_libdir}/nagios/plugins/raf_*

%changelog
* Fri Jan 22 2010 Chris Webster <cjw@ucar.edu> - 1.0-2
- Add raf_ to local commands.  Switch check_ntp to check_ntp_peer
* Sun Aug 23 2009 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
