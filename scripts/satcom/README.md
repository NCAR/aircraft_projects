# Satcom traffic capture and analysis

How much satcom bandwidth a flight used, and where that traffic was going.

**WARNING: THIS CODE HAS BEEN UPDATED SINCE LAST FLOWN. CAREFULLY TEST ALL AIRCRAFT 
INSTALL BEFORE FLY WITH IT**

Three scripts, in the order they are used:

| Script | Where it runs | What it does |
| --- | --- | --- |
| `satcom_capture.sh` | on the aircraft, as root | records traffic crossing the satcom link |
| `analyze-satcom.sh` | on the ground | per-capture and per-flight summaries |
| `satcom-overview.sh` | on the ground | one table of where the traffic went, across flights |

The other scripts here (`launch_iridium`, `run_iridium`, `shutdown_mpds`,
`show_*_log.sh`, …) bring the Iridium and MPDS links up and down and watch their
logs. They are unrelated to the traffic analysis below.

## Capturing, on the aircraft

`satcom_capture.sh` runs `tcpdump` and needs root. It is started by systemd at
boot rather than by hand, so that a capture covers the whole flight and nobody
has to remember to start one — see [Running it at startup](#running-it-at-startup).

**It works out its own interface**, so there is nothing to set per machine. The
traffic that leaves the aircraft goes out via the default route, so the device
carrying that route is the one to capture. On a machine with a single LAN NIC
that is the LAN NIC; on acserver, which emits the NIDAS multicast on a separate
interface, it is the outward-facing `eno8303np0`.

**It refuses to capture, and logs why, if that interface is not on the onboard
network** (`192.168.84.x`). A default route out of some other link — hangar
ethernet on the ramp, say — would otherwise give a capture that looks completely
normal but records the wrong thing. At boot it waits up to a minute for a default
route to appear, since the service can start before the network is ready.

Overrides, for a machine that does not fit the above:

| Variable | Effect |
| --- | --- |
| `INTERFACE=<dev>` | skip detection and capture on `<dev>` |
| `EXPECTED_NET=<prefix>` | address prefix the interface must have (default `192.168.84.`) |
| `WAIT_SECS=<n>` | seconds to wait at boot for a default route (default 60) |

Captures go to `/var/log/satcom-capture/`, up to ten 100 MB files, with only the
first 96 bytes of each packet recorded and traffic that is not leaving the
aircraft filtered out. The script creates that directory if it is missing and
chowns it to `tcpdump:tcpdump` — **`tcpdump` drops privileges to the `tcpdump`
user, so a root-owned directory there will not work.** If the chown could not be
done the script logs a warning, and the fix is:

```sh
sudo mkdir -p /var/log/satcom-capture
sudo chown tcpdump:tcpdump /var/log/satcom-capture
```

Captures are named `traffic<YYYYMMDD_HHMMSS>.pcap0`, `.pcap1`, … — one session,
rotated. Add the machine name when collecting them, as
`traffic<stamp>_<host>.pcap0`; the analysis reads the hostname from there.

At 100 MB per file and ten files there is no realistic chance of the ring buffer
wrapping during a flight, so the start of a flight is not at risk.

### Running it at startup

The capture is a boot-time service so that it is already running before the
flight starts. The unit file, the `systemctl` steps and how to check it took are
in **[INSTALL_LINUX.md](INSTALL_LINUX.md)**.

The Windows machines run [satcom_capture.ps1](satcom_capture.ps1) from Task
Scheduler instead — same behaviour, different plumbing — installed per
**[INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)**.

Two things worth knowing about either:

- **Order it after the network is up** (`Wants=`/`After=network-online.target`).
  The script tolerates starting early — it waits up to `WAIT_SECS` for a default
  route — but it cannot detect an interface that does not exist yet, and it will
  refuse rather than guess.
- **Where the messages go.** Everything the script reports goes both to the
  journal (`journalctl -u <unit>`) and to
  `/var/log/ads/satcom/satcom_capture.log`, so a refusal to capture is visible
  either way. The log line names the interface and address it chose, or the
  reason it declined.

## Analyzing, on the ground

Collect the captures into one directory per flight and run the analysis from the
directory holding them:

```
<root>/
  rf14_20260901/
    traffic20260901_180236_brix01.pcap0
    traffic20260901_180115_acserver.pcap0
    applanix/
      satcom_20260901_181026.pcap        # Windows-side capture, no host in the name
  rf13_20260827/
    ...
```

```sh
cd <root>
./analyze-satcom.sh                       # every rf* flight
./analyze-satcom.sh rf14_20260901         # one flight
./analyze-satcom.sh rf14_20260901/applanix
./analyze-satcom.sh <path>/traffic20260901_180236_brix01.pcap0
./analyze-satcom.sh 20260901_180236       # one capture, by date stamp
```

`rf*` is deliberate — maintenance days are skipped unless you name them.

It writes two kinds of file, next to the captures:

- `satcom-analysis_<stamp>[_<host>].txt` — one per capture: `src => dst: N MB`.
- `satcom-summary_<scope>.txt` — one per flight (or whatever scope was asked
  for): totals, how long the flight was collected for, each onboard machine with
  what it sent and received, and every flow with hostnames alongside addresses.

Options: `--root DIR` if you would rather not `cd`, `--skip-existing` to leave
analysis files already present, `--no-dns` to skip hostname lookups,
`--cache FILE` to move the hostname cache, `--help`. `$SATCOM_ROOT` and
`$SATCOM_PTR_CACHE` set the first and fourth.

Then, for the cross-flight picture:

```sh
./satcom-overview.sh                      # every rf* flight
./satcom-overview.sh rf14_20260901        # one flight, or several
```

This writes `satcom-overview[_<scope>].txt` **to the root** and prints the same
report: each destination with its megabytes, the hours it was observed, and
megabytes per hour, plus a total and an overall rate. Each UCAR/NCAR address is
listed on its own; everything else is grouped by operator, so a content network
spread over hundreds of addresses reads as one line. `--min MB` sets the cutoff
for small rows (default 0.1; `--min 0` shows everything).

The overview reads the summary files and never opens a capture, so re-running it
costs a second — reanalyze only when the captures themselves change.

## The hostname cache

Reverse DNS answers are cached in **`~/.cache/satcom-ptr.tsv`**, a two-column
file of address and name. Override it with `--cache FILE` or `$SATCOM_PTR_CACHE`.
It lives outside the capture tree on purpose, so it is reused wherever the
captures happen to be.

**Addresses with no name are cached too**, as `unknown`. That is what makes a
repeat pass over a season of flights do no lookups at all, but it also means an
address that only became resolvable later stays `unknown`.

**To force fresh lookups, delete the cache file.** It is rebuilt on the next run.
This is also the fix if summaries come back full of `unknown` because they were
first analyzed on a machine without `dig` — the failed lookups will have been
cached, and installing `dig` alone will not clear them.

## Requirements

- **wireshark** — `analyze-satcom.sh` needs `tshark` and `mergecap`. It stops
  if they are missing, and names the install command for the machine it is on
  (`sudo dnf install wireshark-cli` on the aircraft servers,
  `brew install wireshark` on a Mac). `satcom-overview.sh` needs neither.
- **`dig`** — optional, for hostnames. On a minimal Linux install it comes from
  `bind-utils`. Without it the analysis still runs and the summary says why the
  names are missing.

Everything else is bash and the standard command-line tools.

## Tests

```sh
./test/testAnalyzeSatcom.sh
./test/testSatcomOverview.sh
```

Both print a pass/fail count and exit non-zero on failure. They need no
captures, no wireshark and no network, and take about a second. Worth running on
the aircraft machines as well as your laptop — that is where a difference between
BSD and GNU command-line tools would show up.

## Reading the numbers

- **Everything reported left the aircraft.** Multicast, broadcast and
  onboard-to-onboard traffic is excluded even when the capture contains it, so
  totals are smaller than the raw capture — on the MC machines, much smaller. It
  also means flights captured before and after the capture filter was tightened
  can be compared with each other.
- **Collection time is a minimum.** `tcpdump`'s stop time is not recorded
  anywhere, so a flight is timed from when the capture started to its last
  packet.
- **Summing the captures on a flight is correct.** Each machine records only its
  own traffic, so the per-machine figures do not overlap.
- **A flight is only comparable with another if the same machines were
  captured.** acserver carries most of the traffic; a flight where it was not
  captured will look far quieter than one where it was.
- **Overview megabytes are approximate.** They come from the per-flow figures in
  the summary files, rounded to 0.01 MB each. The flight summaries hold the exact
  totals.
