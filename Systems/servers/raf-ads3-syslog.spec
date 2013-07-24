Summary: Additions to syslog config for logging from NIDAS processes.
Name: raf-ads3-syslog
Version: 1.0
Release: 7
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
# BuildRoot is only needed by older rpm versions
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor: UCAR
BuildArch: noarch
Requires: syslog
Source: %{name}-%{version}.tar.gz

%description
Additions to syslog config for logging from NIDAS processes.

%prep
%setup -n %{name}

%build

%install
rm -fr $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc
cp -r etc/logrotate.d $RPM_BUILD_ROOT/etc

%triggerin -- sysklogd rsyslog
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# if SYSLOGD_OPTIONS doesn't exist add it, with a -r  -s " " options
# if it does and it doesn't have -r -s, add -r and -s option

cf=/etc/sysconfig/syslog
if [ -f $cf ]; then
    if ! egrep -q "^[[:space:]]*SYSLOGD_OPTIONS=" $cf; then
        sed -i '${
a###### start %{name}-%{version} ######
aSYSLOGD_OPTIONS="-m 0 -r -s raf.ucar.edu:eol.ucar.edu"
a###### end %{name}-%{version} ######
}' $cf
    else
        sed -i '/^[[:space:]]*SYSLOGD_OPTIONS=/{
# If -r and -s option, done
/-r -s/b
i###### start %{name}-%{version} ######
h
# comment out existing statement
s/.*/# &/p
x
s/SYSLOGD_OPTIONS="[^"]*/& -r -s raf.ucar.edu:eol.ucar.edu:atd.ucar.edu/
a###### end %{name}-%{version} ######
}' $cf
    fi
fi

# for /etc/sysconfig/rsyslog, add -s "" to -c 3.
cf=/etc/sysconfig/rsyslog
if [ -f $cf ]; then
    if ! egrep -q "^[[:space:]]*SYSLOGD_OPTIONS=" $cf; then
        sed -i '${
a###### start %{name}-%{version} ######
aSYSLOGD_OPTIONS="-c 3 -s raf.ucar.edu:eol.ucar.edu:atd.ucar.edu"
a###### end %{name}-%{version} ######
}' $cf
    else
        sed -i '/^[[:space:]]*SYSLOGD_OPTIONS=/{
# If -c 3 -s option, done
/-c 3 -s/b
i###### start %{name}-%{version} ######
h
# comment out existing statement
s/.*/# &/p
x
/-c 3/b c3
s/SYSLOGD_OPTIONS="[^"]*/& -c 3 -s raf.ucar.edu:eol.ucar.edu:atd.ucar.edu/
b
: c3
s/SYSLOGD_OPTIONS="[^"]*/& -s isff.ucar.edu:eol.ucar.edu:atd.ucar.edu/
a###### end %{name}-%{version} ######
}' $cf
    fi
fi

cf=/etc/rsyslog.conf
if [ -f $cf ]; then
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
fi

cf=/etc/syslog.conf
[ -f $cf ] || cf=/etc/rsyslog.conf
sed -i -r '/^\*\.info/{
# Add local5.none to *.info if it is not there
/local5.none/b
s/^([^[:space:]]+)/\1;local5.none/
}' $cf

if ! egrep -q "^local5" $cf; then
cat >> $cf << EOD
local5.info			/var/log/ads3.log
kern.info			/var/log/ads3_kernel.log
EOD
fi

chmod +r /var/log/messages
touch /var/log/ads3.log
touch /var/log/ads3_kernel.log
if [ -x /etc/init.d/syslog ]; then
        /etc/init.d/syslog restart
else
        /etc/init.d/rsyslog restart
fi

%triggerin -- logrotate

if [ -f /etc/cron.daily/logrotate ]; then
    mv /etc/cron.daily/logrotate /etc/cron.hourly
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%config(noreplace) %attr(0755,root,root) /etc/logrotate.d/ads3

%changelog
* Thu Apr 04 2013 Gordon Maclean <maclean@ucar.edu> 1.0-7
- Removed .so from rsyslogd module's names.
* Wed Oct 26 2011 Gordon Maclean <maclean@ucar.edu> 1.0-6
- Removed  debug output to /var/log/ads3_debug.log and /var/log/ads3_kernel_debug.log
* Tue Feb 9 2009 Gordon Maclean <maclean@ucar.edu> 1.0-5
- sed 4.2 (Fedora) doesn't have -c option
* Fri Jan 16 2009 Gordon Maclean <maclean@ucar.edu> 1.0-4
- better support for rsyslog
* Fri Oct 24 2008 Gordon Maclean <maclean@ucar.edu>  1.0-3
- fixed mistakes in log file names
* Sat Oct 12 2008 Gordon Maclean <maclean@ucar.edu>  1.0-2
- added etc/logrotate.d/ads3
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version

