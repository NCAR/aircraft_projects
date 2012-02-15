Summary: Configuration and plugins for nagios
Name: raf-ac-nagios
Version: 1.0
Release: 9
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
# BuildRoot is only needed by older rpm versions
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Requires: nagios nagios-plugins python
Source: %{name}-%{version}.tar.gz

%description
Configuration and additional plugins for RAF aircraft servers.

%prep
%setup -n %{name}

%build

%pre

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_sysconfdir}/init.d
install -d %{buildroot}%{_sysconfdir}/nagios
install -d %{buildroot}%{_sysconfdir}/nagios/objects
install -d %{buildroot}/usr/lib/nagios/plugins

cp etc/init.d/raf_nagios_init           %{buildroot}%{_sysconfdir}/init.d
cp etc/nagios/objects/raf_commands.cfg  %{buildroot}%{_sysconfdir}/nagios/objects
cp etc/nagios/objects/raf_localhost.cfg %{buildroot}%{_sysconfdir}/nagios/objects
cp usr/lib/nagios/plugins/*             %{buildroot}/usr/lib/nagios/plugins

%triggerin -- nagios
# allow all access to nagios.
cf=/etc/nagios/cgi.cfg
sed -i 's/use_authentication=1/use_authentication=0/g' $cf

%post
# commands.cfg in fc11 will move into nagios/objects
cf=/etc/nagios/nagios.cfg
if ! egrep -q "raf_commands" $cf; then
  sed -i 's/commands.cfg/commands.cfg\ncfg_file=\/etc\/nagios\/objects\/raf_commands.cfg/' $cf
fi
sed -i 's/\/localhost.cfg/\/raf_localhost.cfg/' $cf

/sbin/chkconfig --level 345 nagios on
/sbin/chkconfig --add raf_nagios_init
/etc/init.d/nagios restart

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_sysconfdir}/init.d/raf_nagios_init
%{_sysconfdir}/nagios/objects/raf_commands.cfg
%{_sysconfdir}/nagios/objects/raf_localhost.cfg
/usr/lib/nagios/plugins/raf_*

%changelog
* Tue Feb 14 2012 John Wasinger <wasinger@ucar.edu> - 1.0-9
- Updated to support nagios 3.
- Removed 'check_ssh', it is already defined in objects/commands.cfg.
* Thu Feb 09 2012 John Wasinger <wasinger@ucar.edu> - 1.0-8
- Fixed broken path for 64 bit systems.
- Nagios on these systems defined '$USER1$' as /usr/lib64.
- 'noarch' defaults '%{_libdir}' to '/usr/lib'.
* Fri Dec 09 2011 John Wasinger <wasinger@ucar.edu> - 1.0-7
- Now mentions DSM names that responded to pings.
* Wed Nov 30 2011 John Wasinger <wasinger@ucar.edu> - 1.0-6
- Added raf_nagios_init.
- Detect missing compact flash cards in DSMs.
* Mon Jul 18 2011 Chris Webster <cjw@ucar.edu> - 1.0-5
- Display satcom IP address in raf_check_ppp
* Fri Feb 01 2010 Chris Webster <cjw@ucar.edu> - 1.0-4
- check_ppp should check ppp1, not eth3.
- Add raf_check_proc, check for a local process.  Needed because default check_proc can't find something run under python, because python is the process.
* Fri Jan 26 2010 Chris Webster <cjw@ucar.edu> - 1.0-3
- Re-arrange some things.  Add a nidas host to group things better.
- Fix sed in spec to check if change exists first.
- Add check for squid.
* Fri Jan 22 2010 Chris Webster <cjw@ucar.edu> - 1.0-2
- Add raf_ to local commands.  Switch check_ntp to check_ntp_peer
* Sun Aug 23 2009 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
