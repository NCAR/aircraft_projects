Summary: Configuration for selinux on RAF aircraft and labs.
Name: raf-ac-selinux
Version: 1.0
Release: 2
License: GPL
Group: System Environment/Daemons
Url: http://www.eol.ucar.edu/
Packager: Chris Webster <cjw@ucar.edu>
Vendor: UCAR
BuildArch: noarch

%description
Disable SElinux.


%triggerin -- selinux-policy
# %triggerin script is run when a given target package is installed or
# upgraded, or when this package is installed or upgraded and the target
# is already installed.

cf=/etc/selinux/config
if [ -f $cf ]; then
  sed -i -c 's/^SELINUX=enforcing/SELINUX=disabled/' $cf
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%changelog
* Sat Dec  3 2016 Chris Webster <cjw@ucar.edu>
- Correct the triggerin required package
* Wed Apr 13 2016 Chris Webster <cjw@ucar.edu>
- initial version
