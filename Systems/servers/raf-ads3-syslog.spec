Name: raf-ads3-syslog
Version: 1.0
Release: 9
Summary: Additions to syslog config for logging from NIDAS processes.

License: GPL
Source: %{name}-%{version}.tar.gz
Packager: Gordon Maclean <maclean@ucar.edu>
Vendor: UCAR
BuildArch: noarch

Requires: syslog

%description
Additions to rsyslog config and logrotate for logging from NIDAS processes.

%prep
%setup -q -n %{name}

%build

%install
rm -fr $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/%{_sysconfdir}
cp -r etc/* $RPM_BUILD_ROOT/%{_sysconfdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post

%if 0%{?rhel} < 7
if [ -x /etc/init.d/syslog ]; then
        /etc/init.d/syslog restart
else
        /etc/init.d/rsyslog restart
fi
%else
systemctl restart rsyslog.service
%endif

%triggerin -- rsyslog

# %%triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

chmod +r /var/log/messages
touch /var/log/ads3.log
touch /var/log/ads3_kernel.log
chmod +r /var/log/ads3*

# if SYSLOGD_OPTIONS doesn't exist add it, with -s " " option
# edit out obsolete options

restart=false
tmpfile=$(mktemp /tmp/rsyslog_XXXXXX)

cf=/etc/sysconfig/rsyslog
if [ -f $cf ]; then
    md5sum $cf > $tmpfile
    if ! grep -q "^[[:space:]]*SYSLOGD_OPTIONS=" $cf; then
        sed -i '${
a###### start %{name}-%{version} ######
aSYSLOGD_OPTIONS="-s raf.ucar.edu:eol.ucar.edu"
a###### end %{name}-%{version} ######
}' $cf
    else
        sed -r -i '/^[[:space:]]*SYSLOGD_OPTIONS=/{
# Remove -r -c and -m options (obsolete)
/-r/b fix
/-c [0-9]/b fix
/-m [0-9]/b fix
/atd.ucar/b fix
b
:fix
# comment out existing statement, add new
s/.*/# &/
aSYSLOGD_OPTIONS="-s raf.ucar.edu:eol.ucar.edu"
}' $cf
    fi

    md5sum -c $tmpfile --status || restart=true
fi

cf=/etc/rsyslog.conf
if [ -f $cf ]; then
    md5sum $cf > $tmpfile
    # enable these modules
    modules=(imuxsock imklog imudp)
    for mod in ${modules[*]}; do
        sed -i -r '/^[[:space:]]*#[[:space:]]*\$ModLoad[[:space:]]+'$mod'/s/^[[:space:]]*#//' $cf
    done
    # uncomment these statements
    stmts=(UDPServerRun)
    for stmt in ${stmts[*]}; do
        sed -i -r '/^[[:space:]]*#[[:space:]]*\$'$stmt'/s/^[[:space:]]*#//' $cf
    done

    sed -i -r '/^\*\.info/{
# Add local5.none to *.info if it is not there
/local5.none/b
s/^([^[:space:]]+)/\1;local5.none/
}' $cf

    # remove old directives that are now in /etc/rsyslog.d/ads3.conf
    sed -r -i -e '/^local5.*ads3/d' $cf
    sed -r -i -e '/^kern.*ads3/d' $cf

    md5sum -c $tmpfile --status || restart=true
fi

if $restart; then

%if 0%{?rhel} < 7
if [ -x /etc/init.d/syslog ]; then
        /etc/init.d/syslog restart
else
        /etc/init.d/rsyslog restart
fi
%else
systemctl restart rsyslog.service
%endif

fi

rm -f $tmpfile

%triggerin -- logrotate

if [ -f /etc/cron.daily/logrotate ]; then
    mv /etc/cron.daily/logrotate /etc/cron.hourly
fi

%files
%defattr(-,root,root)
%config %attr(0755,root,root) /etc/logrotate.d/ads3
%config %attr(0755,root,root) /etc/rsyslog.d/ads3.conf

%changelog
* Fri Mar 10 2017 Gordon Maclean <maclean@ucar.edu> 1.0-9
- restart rsyslog in post script
* Fri Mar 10 2017 Gordon Maclean <maclean@ucar.edu> 1.0-8
- fixes for rsyslog
* Thu Apr 04 2013 Gordon Maclean <maclean@ucar.edu> 1.0-7
- Removed .so from rsyslogd module's names.
* Wed Oct 26 2011 Gordon Maclean <maclean@ucar.edu> 1.0-6
- Removed  debug output to /var/log/ads3_debug.log and /var/log/ads3_kernel_debug.log
* Tue Feb 10 2009 Gordon Maclean <maclean@ucar.edu> 1.0-5
- sed 4.2 (Fedora) doesn't have -c option
* Fri Jan 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- better support for rsyslog
* Fri Oct 24 2008 Gordon Maclean <maclean@ucar.edu>  1.0-3
- fixed mistakes in log file names
* Sat Oct 11 2008 Gordon Maclean <maclean@ucar.edu>  1.0-2
- added etc/logrotate.d/ads3
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version

