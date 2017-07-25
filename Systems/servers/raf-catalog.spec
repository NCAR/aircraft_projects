Name:           raf-catalog
Version:        0.0.0
Release:        1%{?dist}
Summary:        Dependencies for running Field-Catalog software on RAF acservers

License:        GPLv3+
# URL:            https://github.com/ncareol/catalog-maps
#Source0:        docker-compose-Linux-x86_64-1.11.2.tar.gz
Source: %{name}-%{version}.tar.gz
#Source: %{name}.tar.gz

Requires:       docker
Requires:       httpd
Requires:       git
BuildArch:      x86_64
BuildRoot:      %{_tmppath}/%{name}

%description
Dependencies for running Field-Catalog software on RAF acservers

%prep
%setup -c

# %build

%install

mkdir -p %{buildroot}/%{_bindir}

pwd
ls -la
env
cp raf-catalog/docker-compose-Linux-x86_64-1.11.2 %{buildroot}/%{_bindir}/docker-compose

mkdir -p ${RPM_BUILD_ROOT}/etc/httpd/conf.d ${RPM_BUILD_ROOT}/etc/sysconfig/ ${RPM_BUILD_ROOT}/etc/systemd/system/

cp raf-catalog/etc/httpd/conf.d/osm_tiles_and_catalog.conf ${RPM_BUILD_ROOT}/etc/httpd/conf.d/osm_tiles_and_catalog.conf

cp raf-catalog/etc/systemd/system/catalog-maps.service ${RPM_BUILD_ROOT}/etc/systemd/system/catalog-maps.service

CATALOG_DIRS="${RPM_BUILD_ROOT}/home/catalog/products/incoming/gv ${RPM_BUILD_ROOT}/home/catalog/products/incoming/c130 ${RPM_BUILD_ROOT}/home/catalog/products/jail/gv ${RPM_BUILD_ROOT}/home/catalog/products/jail/c130 ${RPM_BUILD_ROOT}/home/catalog/products/html/gv ${RPM_BUILD_ROOT}/home/catalog/products/html/c130"

mkdir -pv $CATALOG_DIRS ${RPM_BUILD_ROOT}/var/lib/mod_tile ${RPM_BUILD_ROOT}/home/catalog/.ssh/

# SSH: `catuser` pub key, for products2plane

cp raf-catalog/home/catalog/.ssh/id_rsa_catuser.pub ${RPM_BUILD_ROOT}/home/catalog/.ssh/id_rsa_catuser.pub

%files

#
# root files
#
%attr(0755,root,root) %{_bindir}/docker-compose

%defattr(644,catalog,catalog,755)
/etc/httpd/conf.d/osm_tiles_and_catalog.conf
/etc/systemd/system/catalog-maps.service

#
# catalog files
#

#
# entire path to /home/catalog/products needs to be readable by apache user, so make /home/catalog world-readable
#
%attr(755,catalog,catalog) /home/catalog

#%defattr(file perms, user, group, dir perms)
%defattr(644,catalog,catalog,755)
/home/catalog/products
/var/lib/mod_tile
/home/catalog/.ssh/id_rsa_catuser.pub
#
# TODO ?: authorized_keys
#

%pre

_adduser=false

grep -q ^catalog /etc/passwd || _adduser=true

$_adduser && useradd catalog

#
# add docker group, add catalog user to docker group
#
_adddockergroup=false
grep -q ^docker: /etc/group || _adddockergroup=true
$_adddockergroup && groupadd docker
usermod -aG docker catalog

%post
chmod 700 /home/catalog/.ssh

#
# avoid successive entries to /etc/sysconfig/docker
#

_modify_docker_sysconfig=false
egrep -q ^other_args=\'--iptables=false\' /etc/sysconfig/docker || _modify_docker_sysconfig==true
$_modify_docker_sysconfig && echo "other_args='--iptables=false'" >> /etc/sysconfig/docker

systemctl enable docker
systemctl start docker

systemctl enable httpd
systemctl start httpd

systemctl enable catalog-maps

%changelog
* Mon Jul 24 2017 Erik Johnson <ej@ucar.edu> - 0.0.0
- First raf-catalog package
