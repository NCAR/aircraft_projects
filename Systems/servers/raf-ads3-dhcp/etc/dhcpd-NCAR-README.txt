We have created a custom RPM that installs an /etc/dhcpd.conf file tailored to support the various
laptops and DSMs as they arrive onto the aircraft.

The source for this RPM is obtained from our SVN server at:

  http://svn/svn/raf/Systems/servers/raf-ads3-dhcp.spec
  http://svn/svn/raf/Systems/servers/raf-ads3-dhcp/

We have purposely blocked dynamic allocation of IPs to unknown laptops.  This policy gives NCAR's
IT department the authority to 'vet' out the systems before they are introduced to the aircraft's
network.  This 'vetting' process typically entails sweeping the systems for viruses and disabling
automated updates which try to obtain new packages from the internet.

/etc/dhcpd.conf includes several include files.  These files group the following:

/etc/dhcpd-dsms.conf  - a list of mac addresses to DSMs.  Edit this file when board assignments change.
/etc/dhcpd-ac.conf    -
/etc/dhcpd-c130.conf  -
/etc/dhcpd-gv.conf    -
/etc/dhcpd-lab.conf   -
/etc/raf.ucar.edu.key -
