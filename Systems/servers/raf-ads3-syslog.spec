Summary: Additions to syslog config for logging from NIDAS processes.
Name: raf-ads3-syslog
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Gordon Maclean <maclean@ucar.edu>
BuildRoot: /tmp/%{name}-%{version}
Vendor: UCAR
BuildArch: noarch
Requires: syslog

%description
Additions to syslog config for logging from NIDAS processes.

%prep
# %setup -n %{name}

%build

%triggerin -- sysklogd rsyslog
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

# if SYSLOGD_OPTIONS doesn't exist add it, with a -r option
# if it does and it doesn't have -r, add -r option

cf=/etc/sysconfig/syslog
[ -f $cf ] || cf=/etc/sysconfig/rsyslog
if ! egrep -q "^[[:space:]]*SYSLOGD_OPTIONS=" $cf; then
    sed -i -c '${
a###### start %{name}-%{version} ######
aSYSLOGD_OPTIONS="-m 0 -r -s raf.ucar.edu:eol.ucar.edu:atd.ucar.edu"
a###### end %{name}-%{version} ######
}' $cf
else
    sed -i -c '/^[[:space:]]*SYSLOGD_OPTIONS=/{
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

cf=/etc/syslog.conf
[ -f $cf ] || cf=/etc/rsyslog.conf
sed -i -c -r '/^\*\.info/{
# Add local5.none to *.info if it is not there
/local5.none/b
s/^([^[:space:]]+)/\1;local5.none/
}' $cf

if ! egrep -q "^local5" $cf; then
cat >> $cf << EOD
local5.*			/var/log/ads_debug.log
local5.info			/var/log/ads.log
kern.debug			/var/log/ads3_kernel.log
EOD
fi

chmod +r /var/log/messages
/etc/init.d/syslog restart || /etc/init.d/rsyslog restart

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%changelog
* Sun Feb 10 2008 Gordon Maclean <maclean@ucar.edu>
- initial version
