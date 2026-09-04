# Satcom Monitoring Setup (Linux)

Installs the capture on an onboard Linux machine — acserver, an MC brix, or
steam for testing — so that it starts at boot and covers a whole flight.

Linux only. `satcom_capture.sh` reads `/sys/class/net` and runs under systemd,
so it will not work on a Mac. The **analysis** scripts (`analyze-satcom.sh`,
`satcom-overview.sh`) do run on a Mac, and are usually run on the ground rather
than on the aircraft — see [README.md](README.md).

For the Windows machines, see [INSTALL_WINDOWS.md](INSTALL_WINDOWS.md).

## Step 1: Install tcpdump

The capture needs `tcpdump`, and nothing else:

```bash
sudo dnf install tcpdump
```

Only if you also want to **analyze** captures on this machine (normally you do
that on the ground instead):

```bash
sudo dnf install wireshark-cli   # tshark and mergecap, for analyze-satcom.sh
sudo dnf install bind-utils      # dig, so hostnames can be resolved
```

## Step 2: Copy the scripts to the machine

If `aircraft_projects` is checked out, use it. Otherwise copy `satcom_capture.sh`
across. The paths below assume:

```
/home/ads/scripts/satcom/satcom_capture.sh
```

Adjust `ExecStart` in step 4 if it lives somewhere else, and make sure it is
executable:

```bash
chmod +x /home/ads/scripts/satcom/satcom_capture.sh
```

## Step 3: Create the capture directory (optional)

The script creates `/var/log/satcom-capture` itself and chowns it to
`tcpdump:tcpdump`, so this step is only needed if that fails — it logs a warning
if it does. `tcpdump` drops privileges to the `tcpdump` user, so a root-owned
directory will not work.

```bash
sudo mkdir -p /var/log/satcom-capture
sudo chown tcpdump:tcpdump /var/log/satcom-capture
```

## Step 4: Create the systemd service

`/etc/systemd/system/satcom-capture.service`:

```ini
[Unit]
Description=Satcom Traffic Capture
# network.target is not enough: the script needs a default route to work out
# which interface leaves the aircraft.
Wants=network-online.target
After=network-online.target
# The script exits non-zero when it refuses to capture - no default route, or a
# default route out of some link that is not the satcom path. Retry a few times
# in case the network is merely slow to come up, then give up rather than
# restarting every 30 seconds for the rest of the flight.
StartLimitIntervalSec=600
StartLimitBurst=5

[Service]
Type=simple
User=root
ExecStart=/home/ads/scripts/satcom/satcom_capture.sh
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Note the filename is `satcom_capture.sh`, with an underscore.

There is deliberately no `ExecStop`. Analysis is not a shutdown step: it needs
the captures collected together per flight, it needs wireshark installed, and
`analyze-satcom.sh` run with no working directory would fail anyway. Run it on
the ground — see [README.md](README.md).

## Step 5: Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable satcom-capture.service
sudo systemctl start satcom-capture.service
sudo systemctl status satcom-capture.service
```

Once enabled it starts automatically at boot. `tcpdump` writes up to ten 100 MB
files, rotating, so it can be left running.

## Step 6: Check it is actually capturing

The script logs which interface it chose, or why it refused:

```bash
sudo tail /var/log/ads/satcom/satcom_capture.log
sudo journalctl -u satcom-capture.service -n 20
```

A working start looks like:

```
detected interface eno8303np0 (address 192.168.84.2, via the default route)
capturing on eno8303np0 to /var/log/satcom-capture/traffic20260901_180115.pcap
```

And a capture file should appear:

```bash
sudo ls -l /var/log/satcom-capture/
```

If it refused, the log says why. The usual cause is a default route out of a
ground or hangar link rather than the satcom path, which the script declines
because a capture of the wrong interface looks entirely normal afterwards. To
check what it is seeing:

```bash
ip route get 8.8.8.8
```

To capture that interface anyway, set `INTERFACE` in the unit:

```ini
Environment=INTERFACE=eth0
```

## Afterwards

Collect the captures from each machine into one directory per flight, renaming
them to carry the machine name — `traffic<stamp>_<host>.pcap0` — and run the
analysis on the ground. [README.md](README.md) covers that.
