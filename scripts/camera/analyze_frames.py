#!/usr/bin/env python3
"""
Analyze missing frames in forward/left/right camera image directories.

The analysis window is the flight, with two adjustments:

  - it ends at local sunset (Mountain Time) when sunset comes before landing.
    Recording is stopped by hand, in practice about sunset, so frames are not
    expected past it.
  - it starts at the first frame any camera recorded, since the three cameras
    are started together some minutes after takeoff, so that wait is not the
    cameras missing frames.

Pass --no-trim-start to count from takeoff instead.

Times given on the command line are used as the window exactly, with no sunset
cutoff applied. They are for the flights flt_time cannot describe - one with a
refueling landing, say - and so are expected to account for sunset already.
Start trimming still applies to them unless --no-trim-start is given.

Usage (with manual times):
    analyze_frames.py /path/to/images YYMMDD-HHMMSS YYMMDD-HHMMSS

Usage (with flt_time piped input):
    flt_time /path/to/flight.nc | analyze_frames.py /path/to/images

Examples:
    analyze_frames.py . 260729-200002 260730-030401
    flt_time /home/data/INSPYRE/INSPYRErf01.nc | \
        analyze_frames.py /path/to/images/rf01/

Note: Requires 'astral' and 'pytz' libraries
    pip install -r requirements.txt
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from astral import Observer
from astral.sun import sun
import pytz

# Rocky Mountain Metropolitan Airport (KBJC), the RAF base
# Use RMMA to determine astral sunset. INSPYRE flights are all based out
# of RMMA. However, this isn't a great approximation. It would be better to
# use actual aircraft position.
OBSERVER_LATITUDE = 40.0153
OBSERVER_LONGITUDE = -105.2705
OBSERVER_ELEVATION_M = 3048   # 10000 ft; the aircraft sees the sun past the
                              # sea-level horizon, so this pushes sunset later

# How many of the longest gaps to list per camera
TOP_GAPS = 5

# Histogram buckets for gap lengths, in seconds: (label, low, high) with high
# exclusive. The last bucket is open-ended.
GAP_BUCKETS = [
    ("1 s",      1,   2),
    ("2-5 s",    2,   6),
    ("6-30 s",   6,   31),
    ("31-60 s",  31,  61),
    ("1-5 min",  61,  301),
    ("> 5 min",  301, None),
]

def get_sunset_time(date_utc):
    """
    Get sunset time for Boulder/Broomfield, Colorado on the local (Mountain
    Time) date of the given UTC time.

    date_utc: naive datetime in UTC (e.g. the takeoff time)
    Returns: naive datetime in UTC, to match the rest of the script
    """
    observer = Observer(latitude=OBSERVER_LATITUDE,
                        longitude=OBSERVER_LONGITUDE,
                        elevation=OBSERVER_ELEVATION_M)

    mountain = pytz.timezone('America/Denver')

    # The flight date in local time: a takeoff at 16:58 UTC is the morning of
    # the same day in MT, and the sunset that ends it falls on the next UTC day.
    local_date = pytz.UTC.localize(date_utc).astimezone(mountain).date()

    # Ask astral for sunset on that *local* date, then hand it back in UTC
    sunset_mt = sun(observer, date=local_date, tzinfo=mountain)['sunset']
    sunset_utc = sunset_mt.astimezone(pytz.UTC)

    # Return as naive datetime in UTC
    return sunset_utc.replace(tzinfo=None)

def parse_flt_time_input():
    """
    Parse takeoff and landing times from flt_time output on stdin.
    Returns: (start_time, end_time) as datetime objects, or (None, None) if
             not found.
    """
    takeoff = None
    landing = None

    for line in sys.stdin:
        line = line.strip()

        # Match "Takeoff: Wed Jul 29 20:00:02 2026"
        if line.startswith("Takeoff:"):
            match = re.search(r'Takeoff:\s+(\w+)\s+(\w+)\s+(\d+)\s+'
                              r'(\d+):(\d+):(\d+)\s+(\d+)', line)
            if match:
                day_name, month_name, day, hour, minute, second, year = \
                    match.groups()
                # Parse the date string
                date_str = f"{month_name} {day} {hour}:{minute}:{second} {year}"
                try:
                    takeoff = datetime.strptime(date_str, "%b %d %H:%M:%S %Y")
                except ValueError:
                    pass

        # Match "Landing: Thu Jul 30 03:04:01 2026"
        elif line.startswith("Landing:"):
            match = re.search(r'Landing:\s+(\w+)\s+(\w+)\s+(\d+)\s+'
                              r'(\d+):(\d+):(\d+)\s+(\d+)', line)
            if match:
                day_name, month_name, day, hour, minute, second, year = \
                    match.groups()
                # Parse the date string
                date_str = f"{month_name} {day} {hour}:{minute}:{second} {year}"
                try:
                    landing = datetime.strptime(date_str, "%b %d %H:%M:%S %Y")
                except ValueError:
                    pass

    if takeoff and landing:
        return (takeoff, landing)
    return (None, None)

def parse_timestamp(filename):
    """Parse YYMMDD-HHMMSS format from filename."""
    try:
        # Extract just the timestamp part (before the extension)
        name_part = Path(filename).stem
        return datetime.strptime(name_part, "%y%m%d-%H%M%S")
    except (ValueError, AttributeError):
        return None

def find_gaps(timestamps, start_time, end_time):
    """
    Find the runs of consecutive missing seconds in a camera directory.

    timestamps: iterable of datetimes for the frames that are present
    Returns: list of (gap_start, gap_end, length_seconds), in time order.
    gap_start/gap_end are the first and last missing second of the run, so a
    one-second gap has gap_start == gap_end and length 1.
    """
    # Work in whole seconds since start_time; a set also collapses any
    # duplicate timestamps (e.g. both .jpg and .png for the same second)
    present = sorted(
              {int((ts - start_time).total_seconds()) for ts in timestamps})
    last_second = int((end_time - start_time).total_seconds())

    gaps = []
    prev = -1   # the second just before the first expected frame
    # The sentinel closes out a gap that runs to the end of the window
    for sec in present + [last_second + 1]:
        length = sec - prev - 1
        if length > 0:
            gaps.append((start_time + timedelta(seconds=prev + 1),
                         start_time + timedelta(seconds=sec - 1),
                         length))
        prev = sec

    return gaps

def gap_stats(gaps):
    """
    Summarize gap lengths. Returns a dict, or None if there are no gaps.
    """
    if not gaps:
        return None

    lengths = sorted(g[2] for g in gaps)
    n = len(lengths)
    mid = n // 2
    median = lengths[mid] if n % 2 else (lengths[mid - 1] + lengths[mid]) / 2

    histogram = []
    for label, low, high in GAP_BUCKETS:
        count = sum(1 for L in lengths
                    if L >= low and (high is None or L < high))
        histogram.append((label, count))

    return {
        'count': n,
        'total': sum(lengths),
        'min': lengths[0],
        'max': lengths[-1],
        'median': median,
        'mean': sum(lengths) / n,
        'histogram': histogram,
        'longest': sorted(gaps, key=lambda g: (-g[2], g[0]))[:TOP_GAPS],
    }

def format_duration(seconds):
    """Render a gap length as e.g. '45 s' or '2 m 05 s'."""
    if seconds < 60:
        return f"{seconds} s"
    return f"{seconds // 60} m {seconds % 60:02d} s"

def scan_directory(directory):
    """
    Read the frame times out of an image directory.
    Returns: sorted list of datetimes, or None if the directory is missing.
    """
    if not os.path.isdir(directory):
        return None

    timestamps = []
    for f in os.listdir(directory):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            ts = parse_timestamp(f)
            if ts:
                timestamps.append(ts)

    return sorted(timestamps)

def first_frame(timestamps, start_time, end_time):
    """First frame time inside the window, or None if the camera has none."""
    return next((ts for ts in timestamps
                 if start_time <= ts <= end_time), None)

def analyze_timestamps(timestamps, start_time, end_time):
    """
    Count the frames one camera recorded in the window, and find their gaps.

    timestamps: every frame time in that camera's directory, sorted; times
    outside the window are ignored here rather than by the caller
    Returns: dict with expected/actual/missing/percent counts plus the gaps
    """
    in_window = [ts for ts in timestamps if start_time <= ts <= end_time]

    # Calculate expected count (1 per second)
    duration = (end_time - start_time).total_seconds()
    expected_count = int(duration) + 1  # +1 to include both start and end

    gaps = find_gaps(in_window, start_time, end_time)

    # Count the missing seconds from the gaps rather than from the file count,
    # so duplicate timestamps for one second can't hide a hole
    missing_count = sum(g[2] for g in gaps)
    missing_percent = (missing_count / expected_count * 100) \
                          if expected_count > 0 else 0

    return {'expected': expected_count, 'actual': len(in_window),
            'missing': missing_count, 'percent': missing_percent,
            'gaps': gaps}

def print_gap_report(gaps):
    """Print the gap statistics for one camera, indented under its heading."""
    stats = gap_stats(gaps)
    if stats is None:
        print("  Gaps:     none - every expected second has a frame")
        return

    print(f"  Gaps:     {stats['count']:,} "
          f"(a gap is one run of consecutive missing seconds)")
    print(f"    length: min {format_duration(stats['min'])}, "
          f"median {format_duration(int(round(stats['median'])))}, "
          f"mean {stats['mean']:.1f} s, "
          f"max {format_duration(stats['max'])}")

    print("    distribution:")
    for label, count in stats['histogram']:
        if count:
            print(f"      {label:<9} {count:6,}")

    print(f"    longest {len(stats['longest'])}:")
    for gap_start, gap_end, length in stats['longest']:
        print(f"      {gap_start.strftime('%Y-%m-%d %H:%M:%S')} - "
              f"{gap_end.strftime('%H:%M:%S')}  {format_duration(length)}")

def print_usage():
    """Print how to call the script, for a bad argument count."""
    print("Usage (manual times):")
    print("  analyze_frames.py <base_path> <start_time> <end_time>")
    print("  Example: analyze_frames.py . 260729-200002 260730-030401")
    print("  manual times are used as the window exactly, with no "
          "sunset cutoff")
    print()
    print("Usage (with flt_time):")
    print("  flt_time <flight.nc> | analyze_frames.py <base_path>")
    print("  Example: flt_time /home/data/INSPYRE/INSPYRErf01.nc | \\")
    print("               analyze_frames.py /data/rf01/")
    print()
    print("Options:")
    print("  --no-trim-start   Count from takeoff even if the cameras "
          "started later")

def main():
    # Handle two usage patterns:
    # 1. analyze_frames.py <base_path> <start_time> <end_time>  (manual times)
    # 2. flt_time ... | analyze_frames.py <base_path>            (from stdin)
    # Either may be preceded by --no-trim-start.

    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    flags = [a for a in sys.argv[1:] if a.startswith('-')]
    trim_start = '--no-trim-start' not in flags

    unknown = [f for f in flags if f != '--no-trim-start']
    if unknown:
        print(f"Error: unknown option(s): {' '.join(unknown)}")
        sys.exit(1)

    # Manual times are the window the caller asked for and are left alone;
    # times from flt_time are the flight, and get the sunset cutoff applied.
    manual = False

    if len(args) == 1:
        # Read from stdin (flt_time piped input)
        base_path = args[0]
        start_time, end_time = parse_flt_time_input()

        if start_time is None or end_time is None:
            print("Error: Could not parse Takeoff/Landing times from stdin")
            print("Expected input from flt_time command")
            sys.exit(1)

    elif len(args) == 3:
        # Manual time arguments. flt_time cannot describe a flight with a
        # refueling landing, so those are analyzed this way instead.
        manual = True
        base_path = args[0]
        start_str = args[1]
        end_str = args[2]

        # Parse start and end times
        try:
            start_time = datetime.strptime(start_str, "%y%m%d-%H%M%S")
            end_time = datetime.strptime(end_str, "%y%m%d-%H%M%S")
        except ValueError as e:
            print(f"Error parsing timestamps: {e}")
            print("Format should be YYMMDD-HHMMSS (e.g., 260729-200002)")
            sys.exit(1)

    else:
        print_usage()
        sys.exit(1)

    if start_time > end_time:
        print("Error: start_time must be before end_time")
        sys.exit(1)

    # Recording is stopped by hand, and in practice that happens about sunset,
    # so sunset stands in for when recording ended. Frames after it are not
    # expected, and counting them as missing would report the dark end of the
    # flight as one enormous gap.
    #
    # Manual times skip this: they are already the window that was asked for.
    sunset_time = None if manual else get_sunset_time(start_time)

    # Determine effective end time (whichever comes first: landing or sunset)
    effective_end = end_time
    if sunset_time is not None and sunset_time < end_time:
        effective_end = sunset_time

    # Read every camera before reporting on any of them: the window can only
    # start once all three first-frame times are known
    cameras = ['forward', 'left', 'right']
    scans = {camera: scan_directory(os.path.join(base_path, camera))
             for camera in cameras}

    # The three cameras are started together, usually some minutes after
    # takeoff, so the analysis starts at the first frame *any* of them wrote
    # and the wait for that first frame is not counted as missing. A camera
    # that starts later than its neighbours is a different matter: the others
    # were recording, so those frames really are missing.
    firsts = [t for t in (first_frame(tss, start_time, effective_end)
                          for tss in scans.values() if tss) if t]
    effective_start = min(firsts) if (firsts and trim_start) else start_time

    duration = (effective_end - effective_start).total_seconds()
    print(f"\n📊 Frame Analysis Report")
    print(f"{'='*60}")
    print(f"Time Window: {start_time} to {end_time} UTC")
    if manual:
        print("Analysis window: exactly the times given on the command line")
    elif sunset_time < end_time:
        print(f"Analysis limited to: {effective_end} UTC "
              f"(sunset {sunset_time.strftime('%H:%M:%S')}; "
              f"recording is stopped by hand about then)")
    if effective_start > start_time:
        late = (effective_start - start_time).total_seconds()
        print(f"Analysis starts at: {effective_start} UTC "
              f"(first frame on any camera, "
              f"{format_duration(int(late))} after the window opened)")
    print(f"Duration: {duration:.0f} seconds ({duration/3600:.2f} hours)")
    print(f"Expected frames (@ 1 fps): {int(duration) + 1}")
    print(f"{'='*60}\n")

    # Analyze each directory
    results = {}

    for camera in cameras:
        print(f"📷 {camera.upper()}:")

        if scans[camera] is None:
            print(f"  ⚠ Directory not found: "
                  f"{os.path.join(base_path, camera)}")
            print()
            continue

        result = analyze_timestamps(scans[camera], effective_start,
                                    effective_end)
        results[camera] = result

        if result['actual'] == 0:
            print(f"  ⚠ No files found in time window")

        print(f"  Expected: {result['expected']:,} frames")
        print(f"  Actual:   {result['actual']:,} frames")
        print(f"  Missing:  {result['missing']:,} frames "
              f"({result['percent']:.2f}%)")
        print_gap_report(result['gaps'])
        print()

    # Summary
    print(f"{'='*60}")
    print("SUMMARY:")
    for camera in cameras:
        if camera in results:
            percent = results[camera]['percent']
            gaps = results[camera]['gaps']
            bar_length = 40
            filled = int(bar_length * (100 - percent) / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            longest = max((g[2] for g in gaps), default=0)
            plural = '' if len(gaps) == 1 else 's'
            print(f"{camera.upper():6} {percent:6.2f}% missing  {bar}  "
                  f"{len(gaps):,} gap{plural}, "
                  f"longest {format_duration(longest)}")

if __name__ == '__main__':
    main()
