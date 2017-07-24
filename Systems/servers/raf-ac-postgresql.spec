Name: raf-ac-postgresql
Version: 1.0
Release: 1
Summary: Metapackage for aircraft postgresql requirements.
License: GPL

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
  - create read-only user for ads; data (nimbus) user for writing
  - add SQL code to kill all connections before dropping tables

%prep
%setup -q -n %{name}

%install
cp -r var %{buildroot}/

%clean
rm -rf %{buildroot}

%post


%files 
%defattr(-,root,root)

%changelog
* Mon Jun 26 2017 Chris Webster <cjw@ucar.edu> 1.0-1
- Initial hack
* Mon Jul 24 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Few more pieces in place. Not there yet.
