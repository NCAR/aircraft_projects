Name: raf-ac-postgresql
Version: 1.0
Release: 1
Summary: Metapackage for aircraft postgresql requirements.

License: GPL
Packager: Janine Aquino <janine@ucar.edu>
Vendor: UCAR

Requires: postgresql
Requires: postgresql-server
Requires: postgresql-devel
Requires: qt-postgresql

BuildArch: noarch

%description
   Installation and configuration of postgresql for RAF aircraft servers and 
ground stations.
  - install postgresql if not already installed
  - copy postgresql.conf and pg_hba.conf to server
  - create read-only user for ads; data user for writing
  - add SQL code to kill all connections before dropping tables

%pre
%setup -q -n %{name}

%install
cp -r var %{buildroot}/


%post


%files 

%changelog
* Mon Jun 26 2017 Chris Webster <cjw@ucar.edu> 1.0-1
- Initial hack
