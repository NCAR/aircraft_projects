Name: raf-eol-rt-data
Version: 1.0
Release: 2
Summary: Metapackage for requirements specific to eol-rt-data ground server.
Source: %{name}-%{version}.tar.gz
License: GPL

Requires: postgresql
Requires: postgresql-server
Requires: postgresql-devel
Requires: qt-postgresql
Requires: scons
Requires: qt-devel
Requires: nidas
Requires: nidas-devel
Requires: nidas-build
Requires: python-devel
Requires: openssl-devel
Requires: bzip2-devel
Requires: emacs
Requires: pycrypto

BuildArch: noarch

%description
   Configuration of postgresql for RAF ground stations. 
  - install postgresql if not already installed
    - yum install will install missing dependencies
    - rpm -ivh install requires dependencies to be listed on the command line
      or already installed.
  - copy postgresql.conf and pg_hba.conf to server
  - create a new postgresql database cluster (initdb)
  - start the database server (systemctl) as user postgres
  - create read-write user for ads;
  - install other dependencies
  - create platforms database and aircraft-specific databases
  - install crontab in /var/spool/cron/ads so will run as ads user on eol-rt-data

%prep
%setup -q -n %{name}

%pre
su postgres -c "/usr/bin/initdb /var/lib/pgsql/data"
/bin/systemctl enable postgresql.service
/bin/systemctl restart postgresql
/usr/bin/timedatectl set-timezone UTC

%install
cp -r var %{buildroot}/

%post
# Platforms database holds a list of all aircraft we support. Need one DB 
# per aircraft.
su postgres -c "/usr/bin/cat var/lib/pgsql/psql-init.sql | psql"
createdb -U postgres real-time
createdb -U postgres platforms
createdb -U postgres real-time-A10
createdb -U postgres real-time-B146
createdb -U postgres real-time-C130
createdb -U postgres real-time-DC8
createdb -U postgres real-time-DLR
createdb -U postgres real-time-GH
createdb -U postgres real-time-GV
createdb -U postgres real-time-N42RF
createdb -U postgres real-time-N43RF
createdb -U postgres real-time-N49RF
createdb -U postgres real-time-WB57
createdb -U postgres real-time-WKA


%clean
rm -rf %{buildroot}

%files
%defattr(-,postgres,postgres)
%config /var/spool/cron/ads
%config /var/lib/pgsql/data/pg_hba.conf
%config /var/lib/pgsql/data/postgresql.conf
/var/lib/pgsql/psql-init.sql

%changelog
* Fri Sep 22 2017 Janine Aquino <janine@ucar.edu> 1.0-2
- Separate postgresql configuration for aircraft and ground. Ground is here.
- Aircraft is in raf-ac-postgresql rpm.
* Fri Sep 22 2017 Chris Webster <janine@ucar.edu> 1.0-2
- Add Requires for pycrypto.  Used for NOAA AOC python decryption built into udp2sql.
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-2
- Install crontab
- Add a couple requires.
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Initial hack
