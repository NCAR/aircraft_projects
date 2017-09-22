Name: raf-server-common
Version: 1.0
Release: 1
Summary: Metapackage for common configuration for lab and aircraft systems.

License: GPL
Source: %{name}-%{version}.tar.gz

Requires: raf-devel
Requires: raf-ads3-syslog
Requires: raf-ads3-sysctl
Requires: raf-ads-user
Requires: raf-ac-gdm
Requires: raf-ac-selinux
Requires: raf-ac-chrony
Requires: raf-ac-nagios
Requires: raf-ads3-sudoers
Requires: raf-ac-postgresql
Requires: raf-www-control
Requires: ruby
Requires: libdc1394-devel
Requires: kde-baseapps
Requires: nidas-min
Requires: nidas-libs
Requires: nidas-modules
Requires: nidas-autocal
Requires: nidas-configedit
Requires: nidas-daq
Requires: nidas-devel
Requires: nidas-build
Requires: nidas-buildeol
Requires: nidas-ael
Requires: ael-local-dpkgs

BuildArch: noarch

%description
Metapackage for common lab and aircraft server configuration.

%prep
%setup -q -n %{name}


%install

# Install EPEL and EOL repos.  This needs to be done manually before installing this RPM.
#rpm -ivh  http://download.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm 
#rpm -ihv http://www.eol.ucar.edu/software/rpms/eol-repo-epel-1-3.noarch.rpm

# Copy network config scripts.
mkdir -p ${RPM_BUILD_ROOT}/etc/sysconfig/network-scripts
cp etc/sysconfig/network-scripts/ifcfg-em? ${RPM_BUILD_ROOT}/etc/sysconfig/network-scripts


%post
# All servers operate in UTC.
/usr/bin/timedatectl set-timezone UTC
/usr/bin/hostnamectl set-hostname acserver.raf.ucar.edu

dir=/home/local
if [ ! -d $dir ]; then
  mkdir -p $dir/bin $dir/include $dir/lib
  chown -R ads:ads $dir
  chmod g+w $dir/bin $dir/include $dir/lib
  ln -s $dir /opt/local
fi

mkdir -p /home/data
mkdir -p /var/r1
mkdir -p /var/r2
chown ads:ads /home/data /var/r1 /var/r2


cf=/etc/rc.local
if ! grep -q "nimbus.pid" $cf; then
  cat << EO_RC_LOCAL >> $cf

# Perform some basic housekeeping / clean up.
rm -f /tmp/nimbus.pid
rm -f /home/DataBases/postmaster.pid

EO_RC_LOCAL

fi


cf=/etc/hosts.allow
if ! grep -q "128.117" $cf; then
  cat << EO_HOSTS_ALLOW >> $cf
ALL : LOCAL, .ucar.edu, 128.117., 127.0.0.1, 192.168.
EO_HOSTS_ALLOW
fi


%files 
%config %attr(0644,root,root) /etc/sysconfig/network-scripts/ifcfg-em1
%config %attr(0644,root,root) /etc/sysconfig/network-scripts/ifcfg-em2
%config %attr(0644,root,root) /etc/sysconfig/network-scripts/ifcfg-em3
%config %attr(0644,root,root) /etc/sysconfig/network-scripts/ifcfg-em4


%changelog
* Tue Sep 19 2017 Chris Webster <cjw@ucar.edu> 1.0-1
- Initial hack
