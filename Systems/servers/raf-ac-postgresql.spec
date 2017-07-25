Name: raf-ac-postgresql
Version: 1.0
Release: 2
Summary: Metapackage for aircraft postgresql requirements.
Source: %{name}-%{version}.tar.gz
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
    - yum install will install missing dependencies
    - rpm -ivh install requires dependencies to be listed on the command line
      or already installed.
  - copy postgresql.conf and pg_hba.conf to server
  - create a new postgresql database cluster (initdb)
  - start the database server (systemctl) as user postgres
  - create read-only user for ads; data (nimbus) user for writing

%prep
%setup -q -n %{name}

%install
cp -r var %{buildroot}/
sudo -u postgres /usr/bin/initdb /var/lib/pgsql/data
sudo -u postgres /bin/systemctl start postgresql
sudo -u postgres /usr/bin/cat psql-init.sql | sudo -u postgres psql


%clean
rm -rf %{buildroot}

%post


%files 
%defattr(-,postgres,postgres)
/var/lib/pgsql/data/pg_hba.conf
/var/lib/pgsql/data/postgresql.conf
/var/lib/pgsql/psql-init.sql

%changelog
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Attempt to get rpm to do initial database configuration.
* Mon Jul 24 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Few more pieces in place. Not there yet.
* Mon Jun 26 2017 Chris Webster <cjw@ucar.edu> 1.0-1
- Initial hack
