Summary: Configuration for gdm (auto-login) on RAF aircraft and labs.
Name: raf-ac-gdm
Version: 1.0
Release: 1
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch
Requires: gdm

%description
Configuration for gdm to preform auto-login.  Add the following lines to /etc/gdm/custom.conf
[daemon]
TimedLoginEnable=true
TimedLogin=ads
TimedLoginDelay=10

%prep
# %setup -n %{name}

%build

%install
rm -fr $RPM_BUILD_ROOT
%triggerin -- gdm
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

cf=/etc/gdm/custom.conf
if ! egrep -q "TimedLogin" $cf; then
  sed -i -c '/^server/d' $cf
  sed -i -c '/daemon/a TimedLoginEnable=true\nTimedLogin=ads\nTimedLoginDelay=10' $cf
fi


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%changelog
* Mon Apr 11 2016 Chris Webster <cjw@ucar.edu>
- initial version
