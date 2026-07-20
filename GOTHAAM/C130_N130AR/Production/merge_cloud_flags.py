#!/usr/bin/env python3
"""
Merge cloud flag text files into GOTHAAM LRT NetCDF files.

Starts with text files eg
  Cloud_Flag_LiberalDefinition/GOTHAAM-CloudFlag_C130_GOTHAAM{flight}_R0.txt
and merges them into NetCDF files, eg
  LRT/GOTHAAM{flight}.nc
Command line options generalize file locations. However source files must
have text columns: time, cloud_flag, cloud_buffer, cloud_class
"""

import os
import re
import sys
import glob
import argparse
from pathlib import Path
import numpy as np
import netCDF4 as nc

FILL_VALUE = np.float32(-32767.0)

# Variable metadata as specified
VAR_ATTRS = {
    "CLOUDFLG": {
        "units": "bool",
        "long_name": "Cloud Detection Flag",
        "flag_values": np.array([0, 1], dtype=np.float32),
        "flag_meanings": "no_cloud cloud_detected",
        "standard_name": "status_flag",
        "Category": "CloudAndPrecip",
        "DataQuality": "Final",
        "Dependencies": "3 PLWCD_LPO PLWC2DCA_LPI PLWCC"
    },
    "CLOUDBUFFER": {
        "units": "bool",
        "long_name": "Cloud Detection Flag with +/- 3s Buffer",
        "flag_values": np.array([0, 1], dtype=np.float32),
        "flag_meanings": "no_cloud cloud_or_buffer_detected",
        "standard_name": "status_flag",
        "Category": "CloudAndPrecip",
        "DataQuality": "Final",
        "Dependencies": "1 CLOUDFLG",
    },
    "CLOUDCLASS": {
        "units": "none",
        "long_name": "Cloud Classification based on Temperature",
        "flag_values": np.array([0, 2, 3, 4], dtype=np.float32),
        "flag_meanings": "no_cloud warm_cloud_or_haze_or_rain possible_mixed_phase ice_cloud",
        "standard_name": "status_flag",
        "Category": "CloudAndPrecip",
        "DataQuality": "Final",
        "Dependencies": "2 CLOUDFLG ATX",
        "comment": "Classification is temperature based: 2 (T > 0C), 3 (-40C < T < 0C), 4 (T < -40C). Researcher needs to check OAP imagery for verification.",
    },
}


def extract_flight(txt_path):
    """Extract flight identifier like 'rf01' or 'tf02' from text filename."""
    m = re.search(r"[rtf]f[0-9][0-9]",txt_path)
    if m:
        return m.group()
    return None


def merge_one(txt_path, nc_path):
    """Merge a single text file into its corresponding NetCDF."""
    # Read text file (handles Windows line endings)
    data = np.genfromtxt(txt_path, delimiter=",", dtype=np.float64)
    txt_times = data[:, 0].astype(np.int32)
    txt_cloud_flag = data[:, 1].astype(np.float32)
    txt_cloud_buffer = data[:, 2].astype(np.float32)
    txt_cloud_class = data[:, 3].astype(np.float32)

    # The Cloud Flag file should contain columns:
    # time, cloud_flag, cloud_buffer, cloud_class
    # Do some sanity checks on the data read in.
    # right shape?
    if data.ndim != 2 or data.shape[1] != 4:
        raise ValueError(f"{txt_path}: expected 4 columns, got shape {data.shape}")
    # no parse failures (genfromtxt fills bad fields with NaN)
    if np.isnan(data).any():
        bad = np.where(np.isnan(data).any(axis=1))[0]
        raise ValueError(f"{txt_path}: unparseable values on rows {bad.tolist()}")
    # columns 2-4 must be single digits 0-9
    flags = data[:, 1:4]
    if not np.all((flags >= 0) & (flags <= 9) & (flags == np.floor(flags))):
        raise ValueError(f"{txt_path}: cols 2-4 must be single digits 0-9")

    # Open NetCDF in append mode
    ds = nc.Dataset(nc_path, "a")
    nc_times = ds.variables["Time"][:]
    ntime = len(nc_times)

    # Build a lookup: nc_time_value -> index
    time_to_idx = {int(t): i for i, t in enumerate(nc_times)}

    var_names = ["CLOUDFLG", "CLOUDBUFFER", "CLOUDCLASS"]
    txt_arrays = [txt_cloud_flag, txt_cloud_buffer, txt_cloud_class]

    for vname, txt_arr in zip(var_names, txt_arrays):
        # Create variable if it doesn't already exist
        if vname not in ds.variables:
            var = ds.createVariable(vname, "f4", ("Time",), fill_value=FILL_VALUE)
        else:
            var = ds.variables[vname]

        # Initialize with fill values
        out = np.full(ntime, FILL_VALUE, dtype=np.float32)

        # Map text data onto NC time grid
        matched = 0
        for j, t in enumerate(txt_times):
            idx = time_to_idx.get(int(t))
            if idx is not None:
                out[idx] = txt_arr[j]
                matched += 1

        var[:] = out

        # Set attributes
        for attr_name, attr_val in VAR_ATTRS[vname].items():
            var.setncattr(attr_name, attr_val)

        # Compute and set actual_range from non-fill data
        valid = out[out != FILL_VALUE]
        if len(valid) > 0:
            var.setncattr("actual_range",
                          np.array([valid.min(), valid.max()], dtype=np.float32))

    ds.close()
    return matched, len(txt_times), ntime

def parse_args():
    """ Instantiate a command line argument parser """
    parser = argparse.ArgumentParser(
        description="Script to merge cloud flags into production LRT data",
        epilog="Example: %(prog)s -i Cloud_Flag [-o LRT]")
    parser.add_argument( '-b', '--base-dir', type=Path,
        default=Path("/scr/raf/Prod_Data/GOTHAAM"),
        help="Base directory containing files, or dirs with files," +
             "to merge")
    parser.add_argument( '-i', '--source-dir', type=Path,
        default=Path("Cloud_Flag_LiberalDefinition"),
        help="Source subdirectory containing files to be merged")
    parser.add_argument( '-p', '--source-file_pattern', type=str,
        default="GOTHAAM-CloudFlag_C130_GOTHAAM[rtf]f[0-9][0-9]_R?.txt",
        help="Glob pattern for matching input files (default: %(default)s)")
    parser.add_argument( '-o', '--target-dir', type=Path,
        default=Path("LRT"),
        help="Target subdirectory containing files to merge into")
    args = parser.parse_args()

    return args

def main():
    # Parse command line arguments
    args = parse_args()
    basedir = args.base_dir
    SOURCE_DIR = os.path.join(basedir, args.source_dir)
    TARGET_DIR = os.path.join(basedir, args.target_dir)

    print("Merging files in " + SOURCE_DIR + " into " + TARGET_DIR)

    # Find the files to merge
    txt_files = sorted(glob.glob(os.path.join(SOURCE_DIR,
                       args.source_file_pattern)))
    print(f"Found {len(txt_files)} text files")

    for txt_path in txt_files:
        flight = extract_flight(txt_path)
        if flight is None:
            print(f"  SKIP: Could not parse flight from " +
                  f"{os.path.basename(txt_path)}")
            continue

        try:
          project = os.environ["PROJ"]
        except:
          print("PROJ not set; run with export PROJ=<project> && ",
                os.path.basename(sys.argv[0]))
          exit(1)
        nc_path = os.path.join(TARGET_DIR, f"{project}{flight}.nc")
        if not os.path.exists(nc_path):
            print(f"  SKIP: No NetCDF for flight {flight} ({nc_path})")
            continue

        matched, txt_len, nc_len = merge_one(txt_path, nc_path)
        print(f"  {flight}: merged {matched}/{txt_len} text rows into " +
              f"{nc_len} NC timesteps")

    print("Done.")


if __name__ == "__main__":
    main()
