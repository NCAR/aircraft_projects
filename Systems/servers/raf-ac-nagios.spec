Name: raf-ac-nagios
Version: 1.0
Release: 13
Summary: Configuration and plugins for nagios

License: GPL
Source: %{name}-%{version}.tar.gz
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: nagios nagios-plugins python

%description
Configuration and additional plugins for RAF aircraft servers.

%prep
%setup -q -n %{name}

%build

%pre

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_sysconfdir}/init.d
install -d %{buildroot}%{_sysconfdir}/nagios
install -d %{buildroot}/usr/lib64/nagios/plugins

cp etc/init.d/raf_nagios_init   %{buildroot}%{_sysconfdir}/init.d
cp etc/nagios/raf_commands.cfg  %{buildroot}%{_sysconfdir}/nagios
cp etc/nagios/raf_localhost.cfg %{buildroot}%{_sysconfdir}/nagios
cp usr/lib/nagios/plugins/raf_* %{buildroot}/usr/lib64/nagios/plugins

%triggerin -- nagios
# allow all access to nagios.
cf=/etc/nagios/cgi.cfg
sed -i 's/use_authentication=1/use_authentication=0/g' $cf

%post
# commands.cfg in fc11 will move into nagios/objects
cf=/etc/nagios/nagios.cfg
if ! grep -q "/raf_commands.cfg" $cf; then
  sed -i 's/commands.cfg/commands.cfg\ncfg_file=\/etc\/nagios\/raf_commands.cfg/' $cf
fi
if ! grep -q "/raf_localhost.cfg" $cf; then
  sed -i 's/localhost.cfg/localhost.cfg\ncfg_file=\/etc\/nagios\/raf_localhost.cfg/' $cf
fi
if ! grep -q "log_external_commands=1" $cf; then
  sed -i 's/log_external_commands=1/log_external_commands=0/' $cf
fi
if ! grep -q "log_passive_checks=1" $cf; then
  sed -i 's/log_passive_checks=1/log_passive_checks=0/' $cf
fi
if ! grep -q "use_syslog=1" $cf; then
  sed -i 's/use_syslog=1/use_syslog=0/' $cf
fi

/sbin/chkconfig --level 345 nagios on
/sbin/chkconfig --add raf_nagios_init
/etc/init.d/nagios restart

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_sysconfdir}/init.d/raf_nagios_init
%{_sysconfdir}/nagios/raf_commands.cfg
%{_sysconfdir}/nagios/raf_localhost.cfg
/usr/lib64/nagios/plugins/raf_*

%changelog
* Thu Nov 13 2014 Chris Webster <cjw@ucar.edu> - 1.0-13
- In EL7, the plugin directory /usr/lib/nagios moved to /usr/lib64/nagios
* Thu Nov 13 2014 Chris Webster <cjw@ucar.edu> - 1.0-12
- Change logging options in nagios.cfg.
* Mon Mar 05 2012 John Wasinger <wasinger@ucar.edu> - 1.0-11
- Omit non ARCOM based DSMs from the list when checking CF cards.
* Wed Feb 15 2012 John Wasinger <wasinger@ucar.edu> - 1.0-10
- Reverted back to rev 8 folder layout (still supports nagios 2 and 3).
- Created 'aircraft-server' and 'aircraft-services' templates.
- Nagios'es original localhost.cfg left unaltered.
- Like raf_commands.cfg, raf_localhost.cfg adds to nagios'es base definitions.
- 'check_ssh' still removed.  Currently unused.  Introduced natively in nagios 3.
- REINSTALL OF NAGIOS REQUIRED TO FIX /localhost.cfg ALTERATIONS.
* Tue Feb 14 2012 John Wasinger <wasinger@ucar.edu> - 1.0-9
- Updated to support nagios 3.
- Removed 'check_ssh', it is already defined in objects/commands.cfg.
* Thu Feb 09 2012 John Wasinger <wasinger@ucar.edu> - 1.0-8
- Fixed broken path for 64 bit systems.
- Nagios on these systems defined '$USER1$' as /usr/lib64.
- 'noarch' defaults '%%{_libdir}' to '/usr/lib'.
* Fri Dec 09 2011 John Wasinger <wasinger@ucar.edu> - 1.0-7
- Now mentions DSM names that responded to pings.
* Wed Nov 30 2011 John Wasinger <wasinger@ucar.edu> - 1.0-6
- Added raf_nagios_init.
- Detect missing compact flash cards in DSMs.
* Mon Jul 18 2011 Chris Webster <cjw@ucar.edu> - 1.0-5
- Display satcom IP address in raf_check_ppp
* Mon Feb 01 2010 Chris Webster <cjw@ucar.edu> - 1.0-4
- check_ppp should check ppp1, not eth3.
- Add raf_check_proc, check for a local process.  Needed because default check_proc can't find something run under python, because python is the process.
* Tue Jan 26 2010 Chris Webster <cjw@ucar.edu> - 1.0-3
- Re-arrange some things.  Add a nidas host to group things better.
- Fix sed in spec to check if change exists first.
- Add check for squid.
* Fri Jan 22 2010 Chris Webster <cjw@ucar.edu> - 1.0-2
- Add raf_ to local commands.  Switch check_ntp to check_ntp_peer
* Sun Aug 23 2009 Chris Webster <cjw@ucar.edu> - 1.0-1
- initial version
