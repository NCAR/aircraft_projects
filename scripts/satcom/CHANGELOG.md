# Changelog

Changelog for the satcom traffic scripts in `aircraft_projects/scripts/satcom/` —
`satcom_capture.sh`, `analyze-satcom.sh`, `satcom-overview.sh`, and the `test/` suite.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/).
Version numbers are coarse groupings of related work rather than tagged releases;
each section also lists the date of the changes it covers. This changelog starts
at 2.0, which covers the rewrite described below; the original single-capture
`analyze-satcom.sh` is treated as 1.0.

## [2.2] - unreleased

### Changed

- `analyze-satcom.sh`, `satcom-overview.sh`: The output files now state that
  every protocol is included. Traffic is selected by address and never by
  protocol or port, so TCP, UDP — DNS, NTP, QUIC, DTLS — ICMP and everything
  else are counted alike. This was already true and had never been written
  down, which left a reader with no way to tell whether a small UDP figure
  meant little UDP traffic or a filter that had quietly excluded it.

## [2.1] - 2026-09-17

2.0 answered how much each flight sent and where it went. Reading those answers
against the router's own WAN2 counters showed the totals were being asked to
mean something they did not: they counted every byte a machine *addressed* off
the aircraft, including bytes the router dropped and never carried. This release
separates what crossed satcom from what only tried to, and adds the sections
needed to see why the router behaves as it does.

### Added

- `analyze-satcom.sh`: A **Blocked at the router** section, and `--allowed` (or
  `$SATCOM_ALLOWED`) to name the onboard machines the router permits off the
  aircraft. A blocked machine does not know it is blocked: it keeps addressing
  traffic outward, its own capture records it, and until now the analysis counted
  it as off-plane. On RF16 that was 6.60 MB of the 358.77 MB reported — applanix
  6.22 and brix05 0.38 — so the real figure was 352.17 MB. The blocked traffic is
  reported under its own heading rather than discarded, because how much a
  blocked machine is still attempting is worth knowing. There is no default: the
  policy lives in the router, and a guess baked in here would be wrong the first
  time the rules change. Unset, the totals behave exactly as they did before.

- `analyze-satcom.sh`: A warning for any onboard host that sent off-plane traffic
  and received nothing back. TCP and QUIC both answer, so this is either a
  blocked host or a capture that is not seeing its own inbound traffic, and the
  two look identical in the totals. The note says how to tell them apart —
  outbound consisting of nothing but bare SYNs means no connection ever formed,
  because a half-blind capture would still show the host's own ACKs and data.

- `analyze-satcom.sh`: A **Gateway** section, reporting traffic to and from the
  router now that the capture filter keeps `host 192.168.84.1`. These bytes are
  onboard-to-onboard and stay out of the flow totals, which exist to be
  reconciled against the WAN2 counters; folding them in would corrupt the one
  number the summary exists to produce. `$SATCOM_GATEWAY` moves the address.

- `analyze-satcom.sh`: A **DNS** section and a **Router syslog** section, plus a
  verbatim `satcom-syslog_<scope>.txt` beside the summary. Both come out of the
  pass the script already makes over each capture rather than a second read. The
  syslog text is deliberately not parsed: the format belongs to the router and a
  parser written against a guess would report confident nonsense. On RF17 this
  is how the router's conntrack table was found to be full and dropping packets.

- `satcom-overview.sh`: **SENT MB** and **RECV MB** columns beside the total. The
  two directions carry different weight — received bytes reached an onboard host,
  so they crossed the air link, while sent bytes only prove the host put them on
  the LAN. A peer with one column at zero is counted in a note under the table.
  Across the nine flights so far this reads 500.12 MB sent against 4143.29 MB
  received, and it is what makes a working conversation like Fastly (22.74 up,
  70.30 down) obviously different from a one-sided one.

### Fixed

- `analyze-satcom.sh`: Syslog messages were counted twice. When nothing is
  listening on port 514 the destination returns an ICMP port unreachable that
  quotes the datagram, and tshark dissects the quoted copy as a second message.
  RF17 reported 372 where 186 had been sent. Any syslog count in a summary
  generated before this release is doubled.

### Changed

- `satcom-overview.sh`: The destination column is now headed `OFF-PLANE PEER`
  rather than `OFF-PLANE DESTINATION`, since it names both ends of a
  conversation; `COLLECTION (HR)` is shortened to `HOURS` to make room for the
  new columns, and the total row reads `TOTAL (all peers)`. Anything parsing the
  old headings needs updating.

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
