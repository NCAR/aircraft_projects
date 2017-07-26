Name: raf-ac-eolrtdata
Version: 1.0
Release: 1
Summary: Metapackage for requirements specific to eol-rt-data ground server.
Source: %{name}-%{version}.tar.gz
License: GPL

Requires: raf-ac-postgresql

BuildArch: noarch

%description
   Additional configuration of postgresql for RAF ground stations. To be 
installed after raf-ac-postgresql is installed.
  - install raf-ac-postgresql if not already installed
    - yum install will install missing dependencies
    - rpm -ivh install requires dependencies to be listed on the command line
      or already installed.
  - create platforms database

%prep
%setup -q -n %{name}

%install
cp -r var %{buildroot}/

%post
su postgres "/usr/bin/cat var/lib/pgsql/psql-init-eolrtdata.sql | psql"


%clean
rm -rf %{buildroot}

%files 
%defattr(-,postgres,postgres)
/var/lib/pgsql/psql-init-eolrtdata.sql

%changelog
* Tue Jul 25 2017 Janine Aquino <janine@ucar.edu> 1.0-1
- Initial hack
