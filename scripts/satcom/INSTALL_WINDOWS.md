# Satcom Monitoring Setup (Windows)

Installs the capture on onboard Windows machines so that they start at boot and
cover a whole flight.

Note: this was a trial and error learning process. I have tried to recreate what
worked, but I may have missed something. **Use with caution.**

The capture script is [satcom_capture.ps1](satcom_capture.ps1). It is the
counterpart of `satcom_capture.sh` on Linux and behaves the same way: it works
out its own interface from the default route, refuses to capture if that is not
the satcom path, uses the same capture filter and the same 96-byte snaplen, and
stamps file names in UTC.

For the Linux machines, see [INSTALL_LINUX.md](INSTALL_LINUX.md).

All paths below use `C:\satcom-capture`. Do not put this under
`C:\Program Files` — that is ACL-protected, and a service account cannot write
there without an extra `icacls` grant.

## Install npcap (the packet capture driver)

### Download

* Go to `https://npcap.com/download/`
* Download the latest Windows installer (e.g., npcap-1.x.x.exe)
* Run as Administrator

### Installation steps

* Launch the installer
* Installation Options dialog:
  * ✓ Check: "Install Npcap in WinPcap API-compatible Mode"
  * ✓ Check: "Support raw 802.11 traffic (monitor mode)" (optional, but good to have)
  * Leave other defaults as-is
* Click "Install"
* When prompted to restart, click "Yes" (or restart later if needed)
* Verify by opening PowerShell (as Administrator) and running:

```powershell
Get-NetAdapter | Select-Object Name, InterfaceDescription
```

Should see your network adapters listed.

## Install Wireshark

* Confirm win64

```powershell
[Environment]::Is64BitOperatingSystem
```

* Download: `https://www.wireshark.org/download/`
  * Wireshark X.X.X (64-bit) Windows Installer
* Run the installer
* When it gets to "Choose Components," uncheck USBPcap
* Continue with installation
* Finish and restart

## Check the capture works at all

The script picks its own interface, so you do not need to find an interface
number. But it is worth confirming npcap and tshark work before installing the
task. List the interfaces:

```powershell
tshark -D
```

Capture for 10 seconds on the active Ethernet, replacing `1` with its number:

```powershell
mkdir C:\satcom-capture
tshark -i 1 -w "C:\satcom-capture\test.pcap" -a duration:10
Get-ChildItem "C:\satcom-capture\test.pcap"
```

If the file exists and is not empty, npcap is working. Delete it afterwards.
Note that the `tshark -D` numbers move around between reboots, which is why the
script addresses the interface by its npcap device name instead.

## Install the capture script

Copy [satcom_capture.ps1](satcom_capture.ps1) from `aircraft_projects` to:

```
C:\satcom-capture\satcom_capture.ps1
```

The script creates `C:\satcom-capture\logs` for the captures the first time it
runs. Note the filename has an **underscore**, matching the Linux script.

## Allow ads to run batch jobs

* Press Win + R
* Type `gpedit.msc`
* Press Ctrl+Shift+Enter (runs as Admin)
* Enter your password if prompted
* Navigate to: Computer Configuration → Windows Settings → Security Settings → Local Policies → User Rights Assignment
* Find "Log on as a batch job"
* Double-click it
* Click Add User or Group
* Type `ads`
* Click Check Names (should underline it)
* Click OK → OK
* Close and restart the computer

## Run it by hand first

Confirm it works before wiring it to the scheduler.

* Open PowerShell as Admin:
  * Press Win + X
  * Select "Windows PowerShell (Admin)"
* Set the execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

* Run it (`&` tells PowerShell to run the quoted command):

```powershell
& "C:\satcom-capture\satcom_capture.ps1"
```

It logs the interface it chose, or why it refused:

```
detected interface Ethernet [\Device\NPF_{...}] (address 192.168.84.183, via the default route)
capturing to C:\satcom-capture\logs, one file every 3600s, keeping 7 days
```

Leave it a moment, then Ctrl+C and check for output:

```powershell
Get-ChildItem "C:\satcom-capture\logs\"
Get-Content "C:\satcom-capture\satcom_capture.log" -Tail 20
```

You should see a `.pcap` file. If it refused, the log says why — usually a
default route out of a ground or hangar link rather than the satcom path, which
it declines because a capture of the wrong interface looks entirely normal
afterwards. To see what it is looking at:

```powershell
Find-NetRoute -RemoteIPAddress 8.8.8.8
```

To capture that interface anyway, pass it explicitly:

```powershell
& "C:\satcom-capture\satcom_capture.ps1" -Interface "\Device\NPF_{...}"
```

## Create a task to run it at startup

* Press Win + R
* Type `taskschd.msc`
* Press Ctrl+Shift+Enter (runs as Admin)
* Enter your admin password if prompted

### Step-by-step in Task Scheduler

* Right-click Task Scheduler Library → Create Basic Task
  * Name: Satcom Capture
* Click Next
  * Trigger: Select "At startup" → Next
  * Action: Select "Start a program" → Next
  * Program/script:

    ```
    powershell.exe
    ```

  * Add arguments:

    ```
    -NoProfile -ExecutionPolicy Bypass -File "C:\satcom-capture\satcom_capture.ps1"
    ```

* Click Next → Finish
* Right-click the task → Properties → General tab:
  * Click Change User or Group → Type ads → Check Names → OK
  * Check "Run with highest privileges"
  * Check "Run whether user is logged in or not"
* Click OK and enter your password

### Enable history

* Right-click Task Scheduler Library → Properties
* Check the box for "Enable All Tasks History"
* Click OK

### Run the task from the scheduler

* Click Run
* The History tab at the bottom of the window shows whether the task ran and any
  errors
* Exit Task Scheduler

### Verify

```powershell
Get-ScheduledTask -TaskName "Satcom Capture"
Get-ChildItem "C:\satcom-capture\logs\"
Get-Content "C:\satcom-capture\satcom_capture.log" -Tail 20
```

The script's own log is the first place to look. For scheduler-level problems
(the task not starting at all, credentials, permissions):

```powershell
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20
```

## Afterwards

The Windows capture file names — `satcom_<stamp>.pcap` — carry no machine name.
**When collecting them for analysis, put them in a directory named for the
machine**, so `analyze-satcom.sh` can take the hostname from the directory, eg:

```
rf14_20260901/
  applanix/
    satcom_20260901_181026.pcap
```

[README.md](README.md) covers the analysis.
