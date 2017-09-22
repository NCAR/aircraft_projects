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
   Installation and configuration of postgresql for RAF aircraft servers.
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

%pre
su postgres -c "/usr/bin/initdb /var/lib/pgsql/data"
/bin/systemctl enable postgresql.service
/bin/systemctl restart postgresql

%install
cp -r var %{buildroot}/

%post
su postgres -c "/usr/bin/cat var/lib/pgsql/psql-init.sql | psql"
createdb -U postgres real-time


%clean
rm -rf %{buildroot}



%files 
%defattr(-,postgres,postgres)
%config /var/lib/pgsql/data/pg_hba.conf
%config /var/lib/pgsql/data/postgresql.conf
/var/lib/pgsql/psql-init.sql

%changelog
* Fri Sep 22 2017 Janine Aquino <janine@ucar.edu> 1.0-2
- Separate postgresql configuration for aircraft and ground. Aircraft is here.
- Ground is in raf-ac-eolrtdata rpm.
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-2
- Attempt to get rpm to do initial database configuration.
* Mon Jul 24 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Few more pieces in place. Not there yet.
* Mon Jun 26 2017 Chris Webster <cjw@ucar.edu> 1.0-1
- Initial hack
