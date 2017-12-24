Name:           raf-catalog
Version:        1.0
Release:        6%{?dist}
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

cp raf-catalog/docker-compose-Linux-x86_64-1.15.0 %{buildroot}/%{_bindir}/docker-compose

mkdir -p ${RPM_BUILD_ROOT}/etc/httpd/conf.d ${RPM_BUILD_ROOT}/etc/systemd/system/

cp raf-catalog/etc/httpd/conf.d/osm_tiles_and_catalog.conf ${RPM_BUILD_ROOT}/etc/httpd/conf.d/osm_tiles_and_catalog.conf

cp raf-catalog/etc/systemd/system/catalog-maps.service ${RPM_BUILD_ROOT}/etc/systemd/system/catalog-maps.service

cp raf-catalog/etc/systemd/system/irc-bot.service ${RPM_BUILD_ROOT}/etc/systemd/system/irc-bot.service

CATALOG_DIRS="${RPM_BUILD_ROOT}/home/catalog/products/incoming/gv ${RPM_BUILD_ROOT}/home/catalog/products/incoming/c130 ${RPM_BUILD_ROOT}/home/catalog/products/jail/gv ${RPM_BUILD_ROOT}/home/catalog/products/jail/c130 ${RPM_BUILD_ROOT}/home/catalog/products/html/gv ${RPM_BUILD_ROOT}/home/catalog/products/html/c130"

mkdir -p $CATALOG_DIRS ${RPM_BUILD_ROOT}/var/lib/mod_tile ${RPM_BUILD_ROOT}/home/catalog/.ssh/ ${RPM_BUILD_ROOT}/home/catalog/docker/db

# SSH: `catuser` pub key, for products2plane

cp raf-catalog/home/catalog/.ssh/id_rsa_* ${RPM_BUILD_ROOT}/home/catalog/.ssh/
cp raf-catalog/home/catalog/.ssh/config ${RPM_BUILD_ROOT}/home/catalog/.ssh/
cp raf-catalog/home/catalog/.bashrc ${RPM_BUILD_ROOT}/home/catalog/
cp raf-catalog/home/catalog/.gitconfig ${RPM_BUILD_ROOT}/home/catalog/

#
# /etc/sudoers.d/catalog
#
mkdir -p ${RPM_BUILD_ROOT}/etc/sudoers.d
cp raf-catalog/etc/sudoers.d/catalog ${RPM_BUILD_ROOT}/etc/sudoers.d/catalog

%files

#
# root files
#
%attr(0755,root,root) %{_bindir}/docker-compose
%attr(0600,root,root) /etc/sudoers.d/catalog

%defattr(644,catalog,catalog,755)
/etc/httpd/conf.d/osm_tiles_and_catalog.conf
/etc/systemd/system/catalog-maps.service
/etc/systemd/system/irc-bot.service

#
# catalog files
#

#
# entire path to /home/catalog/products needs to be readable by apache user, so make /home/catalog world-readable
#
%attr(755,catalog,catalog) /home/catalog

#%defattr(file perms, user, group, dir perms)
%defattr(644,catalog,catalog,755)
/var/lib/mod_tile
/home/catalog/.ssh/config
/home/catalog/.ssh/id_rsa_catuser.pub
/home/catalog/.ssh/id_rsa_ej_kepler.pub
/home/catalog/.bashrc
/home/catalog/.gitconfig
/home/catalog/docker/db

#
# make /home/catalog/products group eol and group writable, so that ads can write files
#
%attr(775,catalog,eol) /home/catalog/products

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


#
# add eol group, add catalog user to eol group
#
_addeolgroup=false
grep -q ^eol: /etc/group || _addeolgroup=true
$_addeolgroup && groupadd eol
usermod -g eol catalog

#
# add /catalog symbolic link
#
_addcataloglink=false
[ -L /catalog ] || _addcataloglink=true
$_addcataloglink && ln -s /home/catalog/products /catalog

%post
chmod 700 /home/catalog/.ssh

systemctl enable docker
systemctl start docker

systemctl enable httpd
systemctl start httpd

systemctl enable catalog-maps
systemctl enable irc-bot

#
# ~catalog/.ssh/authorized_keys
#

touch /home/catalog/.ssh/authorized_keys

if ! grep -q catuser /home/catalog/.ssh/authorized_keys ; then
  cat /home/catalog/.ssh/id_rsa_catuser.pub >> /home/catalog/.ssh/authorized_keys
fi

if ! grep -q kepler /home/catalog/.ssh/authorized_keys ; then
  cat /home/catalog/.ssh/id_rsa_ej_kepler.pub >> /home/catalog/.ssh/authorized_keys
fi

if ! grep -q gstoss-macbook /home/catalog/.ssh/authorized_keys ; then
  cat /home/catalog/.ssh/id_rsa_gstoss_macbook.pub >> /home/catalog/.ssh/authorized_keys
fi

if ! grep -q loehrer@shiraz /home/catalog/.ssh/authorized_keys ; then
  cat /home/catalog/.ssh/id_rsa_loehrer_shiraz.pub >> /home/catalog/.ssh/authorized_keys
fi

echo_notice () {
  echo
  echo '# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #'
  echo
  echo '  NOTICE: '
  echo
  echo "    $1"
  echo
  echo '# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #'
  echo
}

#
# check for existence of ~catalog/.ssh/id_rsa, if not, echo message to set it up
#
if [ ! -s ~catalog/.ssh/id_rsa ] ; then
  echo_notice '~catalog/.ssh/id_rsa does not exist or is empty. Please set up a valid SSH key for the catalog user.'
fi

#
# check if /var/lib/mod_tile is empty, if it is, echo message to populate it
#
if [ ! -d /var/lib/mod_tile/default ] || [ ! "$(ls -A /var/lib/mod_tile/default)" ] ; then
  echo_notice '/var/lib/mod_tile/default does not exist or is empty. Please populate it w/ OpenStreetMap tiles, e.g. from /scr/ctm/ej/osm/mod_tile*.tar'
fi

chown catalog:catalog /home/catalog/.ssh/authorized_keys

%changelog
* Sat Dec 23 2017 Erik Johnson <ej@ucar.edu> - 1.0-6
- CatalogMaps native: switch from rbenv to chruby
* Fri Dec 22 2017 Erik Johnson <ej@ucar.edu> - 1.0-5
- add accommodations for running CatalogMaps natively w/ rbenv
* Fri Dec 15 2017 Erik Johnson <ej@ucar.edu> - 1.0-4
- add config for SSH alias, github-catalog-ingest, for catalog user
* Thu Nov 08 2017 Erik Johnson <ej@ucar.edu> - 1.0-3
- systemctl enable irc-bot
* Thu Nov 08 2017 Erik Johnson <ej@ucar.edu> - 1.0-2
- Add systemd unit file for irc-bot
- sudoers.d/catalog: add commands for managing irc-bot and reviewing its journal logs
- Remove code for /etc/sysconfig/docker-- no longer used on RHEL 7
* Wed Nov 08 2017 Erik Johnson <ej@ucar.edu> - 1.0-1
- promote version to 1.0
- add dns config to /etc/sysconfig/docker
* Thu Aug 17 2017 Erik Johnson <ej@ucar.edu> - 0.1.7
- ~/.bashrc: use AIRCRAFT for hostname in PS1, alias ll='ls -la'
* Thu Aug 03 2017 Erik Johnson <ej@ucar.edu> - 0.1.6
- Add loehrer@shiraz SSH key to ~catalog/.ssh/authorized_keys
* Wed Aug 02 2017 Erik Johnson <ej@ucar.edu> - 0.1.5
- Add gstoss-macbook SSH key to ~catalog/.ssh/authorized_keys
- Add ej-friendly bash aliases to ~catalog/.bashrc
* Mon Jul 31 2017 Erik Johnson <ej@ucar.edu> - 0.1.4
- catalog user:
- revert method of setting CATALOG_GID, since eol is primary group
- fix typo
* Mon Jul 31 2017 Erik Johnson <ej@ucar.edu> - 0.1.3
- catalog-user group friendliness:
- add group eol to catalog user as its primary group
- ensure that ~catalog/products has group-write permissions and eol group
- set catalog user's umask to 002
- set CATALOG_GID to eol's gid
* Fri Jul 28 2017 Erik Johnson <ej@ucar.edu> - 0.1.2
- build: remove debugging statements and remove --verbose flags from commands
* Fri Jul 28 2017 Erik Johnson <ej@ucar.edu> - 0.1.1
- Add conditional post-install messages re: ~catalog/.ssh/id_rsa and /var/lib/mod_tile
- /etc/sudoers/catalog: add journalctl -u catalog-maps* for catalog user
* Fri Jul 28 2017 Erik Johnson <ej@ucar.edu> - 0.1.0
- Docker Compose: update to latest release: 1.15.0
- Git: add ej-friendly git aliases
- Docker: add ~catalog/docker/db volume directory for db (mysql) service
* Thu Jul 27 2017 Erik Johnson <ej@ucar.edu> - 0.0.7
- catalog-maps.service: load catalog user's environment when starting
- sudoers/catalog: add commands to manage catalog-maps.service as catalog user
* Wed Jul 26 2017 Erik Johnson <ej@ucar.edu> - 0.0.6
- add /etc/sudoers.d/catalog
* Wed Jul 26 2017 Erik Johnson <ej@ucar.edu> - 0.0.5
- Fixes for ~catalog/.bashrc and ~catalog/.ssh/authorized_keys
* Wed Jul 26 2017 Erik Johnson <ej@ucar.edu> - 0.0.4
- Add catuser (products2plane) and ej SSH pub keys to ~catalog/.ssh/authorized_keys
* Tue Jul 25 2017 Erik Johnson <ej@ucar.edu> - 0.0.3
- catalog-maps.service: fix paths to docker-compose executable
* Tue Jul 25 2017 Erik Johnson <ej@ucar.edu> - 0.0.1
- ~catalog/.bashrc: dynamically populate CATALOG_UID/GID, CATALOG_PLANE environment variables, for use by Docker Compose
- ~catalog/.bashrc: add short aliases for common commands
* Mon Jul 24 2017 Erik Johnson <ej@ucar.edu> - 0.0.0
- First raf-catalog package
