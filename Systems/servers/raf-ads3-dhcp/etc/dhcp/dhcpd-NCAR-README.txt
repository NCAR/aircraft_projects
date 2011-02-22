
Some info on the raf-*-dhcp RPMs.

The source for this RPM is obtained from our SVN server at:

  http://svn/svn/raf/Systems/servers/raf-ads3-dhcp.spec
  http://svn/svn/raf/Systems/servers/raf-ads3-dhcp/

The raf-ads3-dhcp.spec file builds three RPMS:
    raf-gv-dhcp
    raf-c130-dhcp
    raf-lab-dhcp

/etc/dhcpd.conf is owned by the dhcp RPM which comes with RedHat.

Two RPMs cannot own the same file, so rad-*-dhcp cannot have
its own version of /etc/dhcpd.conf.  Instead, raf-*-dhcp contains
a triggerin script, which is run when the package is installed.
This script checks the system /etc/dhcpd.conf file, and replaces
its contents with several include statements, if they are not found
already.

/etc/dhcpd.conf in raf-gv-dhcp does these includes:
    include "/etc/dhcpd-ac.conf";
    include "/etc/dhcpd-gv.conf";
    include "/etc/dhcpd-dsms.conf";
    include "/etc/dhcpd-local.conf";

/etc/dhcpd.conf in raf-c130-dhcp does the same, except substituting
dhcp-c130.conf for dhcp-gv.conf

/etc/dhcpd.conf in raf-lab-dhcp does these includes:
    include "/etc/dhcpd-lab.conf";
    include "/etc/dhcpd-dsms.conf";
    include "/etc/dhcpd-local.conf";


/etc/dhcpd-ac.conf   - The first file included in /etc/dhcpd.conf on aircraft,
    containing the global declarations for aircraft.
/etc/dhcpd-lab.conf   - The first file included in /etc/dhcpd.conf on lab
    systems.

/etc/dhcpd-c130.conf  - any special config for C130. If we do things right
    we may not need different files for GV and C130.
/etc/dhcpd-gv.conf  - any special config for GV. If we do things right
    we may not need different files for GV and C130.

/etc/dhcpd-dsms.conf  - a list of mac addresses to DSMs.  Edit this file
    when board assignments change. This file is used on A/C and in the lab.

/etc/dhcpd-local.conf  - This file is not checked into SVN and is not
    part of the RPM. Add temporary, project-specific, configs here.

/etc/raf.ucar.edu.key - Key file generated automatically by RPM triggerin
    script. Shouldn't need to be changed.
