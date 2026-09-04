# Changelog

Changelog for the satcom traffic scripts in `aircraft_projects/scripts/satcom/` —
`satcom_capture.sh`, `analyze-satcom.sh`, `satcom-overview.sh`, and the `test/` suite.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/).
Version numbers are coarse groupings of related work rather than tagged releases;
each section also lists the date of the changes it covers. This is the first
changelog for these scripts, so 2.0 covers the rewrite described below and the
original single-capture `analyze-satcom.sh` is treated as 1.0.

## [2.0] - 2026-09-04

The original script answered "what is in this one capture file". The question
being asked of it was really "how much satcom bandwidth did each flight use, and
where was it going" — which needs whole flights rather than single captures,
only the traffic that actually left the aircraft, and hostnames rather than bare
addresses. This release is that shift.

### Added

- `analyze-satcom.sh`: Analyzes whole flights. With no argument it processes
  every research flight under the capture root; it also accepts a single flight
  directory, a subdirectory, one capture file, or a capture's date stamp. Each
  capture still gets its own analysis file, and each flight now also gets a
  summary that combines every capture taken on it.

- `analyze-satcom.sh`: Reports hostnames alongside addresses, so a summary reads
  `eol-hurricane.eol.ucar.edu` rather than `128.117.43.128`. Onboard machines are
  identified from the captures themselves rather than from a static host table,
  which covers the laptops on DHCP addresses that no such table could name.
  Addresses that cannot be named are listed as unknown rather than quietly
  omitted, and when reverse DNS is unavailable altogether the summary says so
  instead of leaving a page of unknowns unexplained.

- `analyze-satcom.sh`: Excludes traffic that never left the aircraft — multicast,
  broadcast, and onboard-to-onboard — regardless of whether the capture was
  filtered when it was taken. On the mission-computer captures this is the
  difference between 103 MB of recorded traffic and the 7.8 MB that actually went
  over satcom, and it makes flights captured before and after the capture-time
  filter change comparable with each other.

- `analyze-satcom.sh`: Reports how long each flight was collected for, so the
  volume figures can be read as a rate. Collection time starts when the capture
  started rather than when its first packet arrived, so a quiet host still
  reports the hours it was watching and stays distinguishable from one whose
  capture died early.

- `analyze-satcom.sh`: Reads the Windows-side captures (`applanix/`) as well as
  the Linux ones, despite their different file naming, and treats a capture that
  tcpdump rotated across several files as the single session it was.

- `analyze-satcom.sh`: `--skip-existing` to leave analysis files already present,
  `--no-dns` to skip name lookups, `--root` and `--cache` to say where the
  captures and the hostname cache live, and `--help`.

- `satcom-overview.sh`: New. Rolls the flight summaries up into one table of
  where off-plane traffic goes — destination, megabytes, hours collected, and
  megabytes per hour — with a column total and an overall rate. Each UCAR/NCAR
  address is listed separately; everything else is grouped by operator so that a
  content network spread over hundreds of addresses reads as one line. Hours are
  counted only for the flights a destination actually appeared in, so a host
  captured on some flights and not others is not judged against time it was
  never observed. It reads the existing summary files and never opens a capture,
  so the grouping can be changed and rerun in a second without reanalyzing
  anything.

- `satcom_capture.ps1`: New, though not new work — this is the Windows capture
  that had been living as a code block in the install notes, now a script in its
  own right. Windows needs its own script (PowerShell and tshark rather than
  bash and tcpdump, and an entirely different way of naming an interface), but
  it now behaves like the Linux one: same capture filter, same 96-byte snaplen,
  its own interface found from the default route rather than a tshark interface
  number that moves between reboots, the same refusal when that interface is not
  the satcom path, and file names stamped in UTC. That last one had been relying
  on the machine happening to be set to UTC.

- `README.md`, `INSTALL_LINUX.md`, `INSTALL_WINDOWS.md`: How to install the
  capture on each platform, what the analysis writes and how to read it, where
  the hostname cache lives and when to delete it. The systemd unit previously
  named a script that does not exist and ran the analysis at shutdown, where it
  could not work.

- `test/testAnalyzeSatcom.sh`, `test/testSatcomOverview.sh`: Test suites for both
  scripts, covering which traffic counts as having left the aircraft, how
  captures are matched to hostnames and collection times, how destinations are
  grouped, and the scope and option handling of each script. They need no
  captures, no wireshark and no network, and run in about a second.

### Updated

- `satcom_capture.sh`: Finds its own interface instead of having one edited into
  the script per machine. The traffic that leaves the aircraft goes out via the
  default route, so that is the interface captured — which is the LAN card on a
  machine that has one, and the outward-facing card on acserver, without either
  needing to be named. It refuses to capture, and logs why, when that interface
  is not on the onboard network, so a hangar or ground link being up cannot
  quietly produce a capture of the wrong thing. It also tolerates being started
  before the network is ready, which it has to since it runs at boot, and it now
  creates the capture directory with the ownership `tcpdump` needs.

- `analyze-satcom.sh`: No longer has to be told which capture to work on, and no
  longer has to be run from inside the capture directory. Paths are no longer
  hardcoded: the capture root defaults to the working directory and can be
  pointed elsewhere, and the hostname cache lives outside the capture tree so it
  is reused wherever the captures happen to be.

- `analyze-satcom.sh`: Hostname lookups are cached between runs, so a repeat pass
  over a season of flights makes no network queries at all.

### Fixed

- `analyze-satcom.sh`: Two captures whose file names differed only in a host
  suffix could both be pulled into one analysis, counting the same traffic twice.
