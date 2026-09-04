<#
.SYNOPSIS
    Log traffic getting off the plane, on Windows. Counterpart to
    satcom_capture.sh, which does the same job on Linux.

.DESCRIPTION
    Started by Task Scheduler at startup, so that a capture covers the whole
    flight. See INSTALL_WINDOWS.md for the task and how to install it. Not
    meant to be run interactively, though running it by hand is how you check
    it works.

    Behaves like the Linux script wherever Windows allows:

      - Finds its own interface, rather than a hardcoded tshark index. The
        traffic that leaves the aircraft goes out via the default route, so
        that is the interface to capture. Addressed by npcap device name
        rather than by the -D number, because those numbers move around.
      - Refuses to capture, and logs why, if that interface is not on the
        onboard network. A capture of the hangar link looks perfectly valid
        afterwards and answers nothing.
      - Waits for a default route at startup rather than dying on the race.
      - Same capture filter, and the same 96-byte snaplen.
      - Stamps file names in UTC, so they line up with the Linux captures and
        with what the analysis expects.

    Writes one file an hour to $LogDir. When collecting these for analysis,
    put them in a directory named for the machine - the file names carry no
    host name, so analyze-satcom.sh takes it from the directory.

.NOTES
    Requires npcap and Wireshark (for tshark.exe). Run with highest privileges.
#>

[CmdletBinding()]
param(
    # Where the captures and this script's log go. Deliberately not under
    # C:\Program Files, which is ACL-protected and needs an icacls grant
    # before a service account can write to it.
    [string] $BaseDir      = 'C:\satcom-capture',
    [string] $TsharkPath   = 'C:\Program Files\Wireshark\tshark.exe',

    # The detected interface must have an address starting with this, or the
    # default route is not the satcom path.
    [string] $ExpectedNet  = '192.168.84.',

    # Skip detection and capture on this npcap device or interface alias.
    [string] $Interface    = '',

    [int]    $WaitSeconds  = 60,      # startup wait for a default route
    [int]    $FileSeconds  = 3600,    # seconds per capture file
    [int]    $KeepDays      = 7,      # delete captures older than this
    [string] $ProbeAddress = '8.8.8.8'
)

$ErrorActionPreference = 'Stop'

$LogDir  = Join-Path $BaseDir 'logs'
$LogFile = Join-Path $BaseDir 'satcom_capture.log'

# Same filter as the Linux script, and it must stay that way. Excludes traffic
# that is not leaving the aircraft:
#   - onboard to onboard on 192.168.84.0/24
#   - onboard to onboard on 192.168.1.0/24
#   - all multicast, 224.0.0.0/4, in either direction (the NIDAS data streams,
#     mDNS, IGMP, SSDP)
# Broadcast is not excluded here, so it is still in the captures; the analysis
# drops it, along with anything else local that gets through.
$CaptureFilter = 'not (src net 192.168.84.0/24 and dst net 192.168.84.0/24) and not (src net 192.168.1.0/24 and dst net 192.168.1.0/24) and not (src net 224.0.0.0/4 or dst net 224.0.0.0/4)'

New-Item -ItemType Directory -Force -Path $BaseDir, $LogDir | Out-Null

function Write-Log {
    param([string] $Message)
    $line = "{0} {1}" -f (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss UTC'), $Message
    Write-Output $line
    Add-Content -Path $LogFile -Value $line
}

<#
    The npcap device name and source address the machine would use to reach off
    the aircraft. Find-NetRoute is the direct equivalent of `ip route get`: it
    resolves the routing decision rather than listing candidate routes, so a
    machine with more than one default route gives the answer the traffic will
    actually take. Nothing is transmitted.
#>
function Get-OutboundInterface {
    try {
        $route = Find-NetRoute -RemoteIPAddress $ProbeAddress -ErrorAction Stop
    } catch {
        return $null
    }
    $index = ($route | Select-Object -First 1).InterfaceIndex
    $src   = ($route | Where-Object { $_.IPAddress } | Select-Object -First 1).IPAddress
    if (-not $index) { return $null }

    $adapter = Get-NetAdapter -InterfaceIndex $index -ErrorAction SilentlyContinue
    if (-not $adapter) { return $null }

    [pscustomobject]@{
        Device = '\Device\NPF_' + $adapter.InterfaceGuid
        Alias  = $adapter.Name
        Source = $src
    }
}

if (-not (Test-Path $TsharkPath)) {
    Write-Log "tshark not found at $TsharkPath - not capturing. Install Wireshark, or pass -TsharkPath."
    exit 1
}

if ($Interface) {
    $device = $Interface
    Write-Log "using forced interface $device (-Interface was given, no detection)"
} else {
    # Task Scheduler starts this at boot, so the default route may not exist yet.
    $waited = 0
    $found  = $null
    while ($true) {
        $found = Get-OutboundInterface
        if ($found) { break }
        if ($waited -ge $WaitSeconds) { break }
        Start-Sleep -Seconds 5
        $waited += 5
    }

    if (-not $found) {
        Write-Log "no default route after ${WaitSeconds}s, so there is no way to tell which interface leaves the aircraft - not capturing"
        exit 1
    }
    if ($waited -gt 0) { Write-Log "waited ${waited}s for a default route" }

    if (-not ("$($found.Source)".StartsWith($ExpectedNet))) {
        Write-Log ("refusing to capture: traffic off the aircraft would leave by {0} from {1}, which is not on {2}x - that is not the satcom path (is a ground or hangar link up?). Pass -Interface '{3}' to capture it anyway." -f `
            $found.Alias, $(if ($found.Source) { $found.Source } else { 'an unknown address' }), $ExpectedNet, $found.Device)
        exit 1
    }

    $device = $found.Device
    Write-Log ("detected interface {0} [{1}] (address {2}, via the default route)" -f $found.Alias, $device, $found.Source)
}

Write-Log "capturing to $LogDir, one file every ${FileSeconds}s, keeping ${KeepDays} days"

# A tshark that exits immediately - bad device, npcap not loaded, no permission -
# would otherwise spin this loop as fast as it can create files.
$consecutiveFailures = 0

while ($true) {
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss')
    $file  = Join-Path $LogDir "satcom_$stamp.pcap"
    $began = Get-Date

    & $TsharkPath -i $device -w $file -a "duration:$FileSeconds" -s 96 -f $CaptureFilter 2>&1 |
        ForEach-Object { Write-Log "tshark: $_" }

    $ranFor = ((Get-Date) - $began).TotalSeconds
    if ($ranFor -lt 10) {
        $consecutiveFailures++
        Write-Log "tshark exited after $([int]$ranFor)s (exit code $LASTEXITCODE) - attempt $consecutiveFailures"
        if ($consecutiveFailures -ge 5) {
            Write-Log "tshark keeps failing immediately - giving up rather than filling the disk with empty captures"
            exit 1
        }
        Start-Sleep -Seconds 30
    } else {
        $consecutiveFailures = 0
    }

    Get-ChildItem (Join-Path $LogDir 'satcom_*.pcap') -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$KeepDays) } |
        Remove-Item -ErrorAction SilentlyContinue
}
