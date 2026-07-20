#!/usr/bin/env python3
"""
Merge cloud flag text files into GOTHAAM LRT NetCDF files.

Text files: Cloud_Flag_LiberalDefinition/GOTHAAM-CloudFlag_C130_GOTHAAM{flight}_R0.txt
NetCDF files: LRT/GOTHAAM{flight}.nc

Text columns: time, cloud_flag, cloud_buffer, cloud_class
"""

import os
import glob
import numpy as np
import netCDF4 as nc

BASE = "/scr/raf/Prod_Data/GOTHAAM"
TXT_DIR = os.path.join(BASE, "Cloud_Flag_LiberalDefinition")
NC_DIR = BASE 
## os.path.join(BASE, "LRT")

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
    basename = os.path.basename(txt_path)
    # Pattern: GOTHAAM-CloudFlag_C130_GOTHAAM{flight}_R0.txt
    prefix = "GOTHAAM-CloudFlag_C130_GOTHAAM"
    suffix = "_R0.txt"
    if basename.startswith(prefix) and basename.endswith(suffix):
        return basename[len(prefix):-len(suffix)]
    return None


def merge_one(txt_path, nc_path):
    """Merge a single text file into its corresponding NetCDF."""
    # Read text file (handles Windows line endings)
    data = np.genfromtxt(txt_path, delimiter=",", dtype=np.float64)
    txt_times = data[:, 0].astype(np.int32)
    txt_cloud_flag = data[:, 1].astype(np.float32)
    txt_cloud_buffer = data[:, 2].astype(np.float32)
    txt_cloud_class = data[:, 3].astype(np.float32)

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


def main():
    txt_files = sorted(glob.glob(os.path.join(TXT_DIR, "GOTHAAM-CloudFlag_C130_GOTHAAM*_R0.txt")))
    print(f"Found {len(txt_files)} text files")

    for txt_path in txt_files:
        flight = extract_flight(txt_path)
        if flight is None:
            print(f"  SKIP: Could not parse flight from {os.path.basename(txt_path)}")
            continue

        nc_path = os.path.join(NC_DIR, f"GOTHAAM{flight}.nc")
        if not os.path.exists(nc_path):
            print(f"  SKIP: No NetCDF for flight {flight} ({nc_path})")
            continue

        matched, txt_len, nc_len = merge_one(txt_path, nc_path)
        print(f"  {flight}: merged {matched}/{txt_len} text rows into {nc_len} NC timesteps")

    print("Done.")


if __name__ == "__main__":
    main()
