#!/usr/bin/env python3
"""
ubx2rinex.py

Combine all UBX files in a directory and convert to RINEX for OPUS,
using RTKLIB's convbin tool. Cross-platform: works on Linux and Windows.
Assumes dual-frequency L1/L2 data.
"""
import sys
import os
import shutil
import argparse
import subprocess


def find_tool(names):
    """Return the first tool in PATH matching one of the names, or None."""
    for name in names:
        path = shutil.which(name)
        if path:
            return name
    return None


def combine_ubx(input_files, combined_path):
    with open(combined_path, 'wb') as wfd:
        for fn in input_files:
            with open(fn, 'rb') as fd:
                shutil.copyfileobj(fd, wfd)


def run_convbin(combined, out_obs, out_nav):
    cmd = [
        "convbin", combined,
        "-r", "ubx",
        "-o", out_obs,
        "-n", out_nav,
        "-f", "3",  # dual-frequency L1/L2
        "-v", "3.04",  # RINEX version 3.04
        "-hm", "UBX_STATION",  # marker name
        "-hn", "001",  # marker number
        "-ht", "GEODETIC",  # marker type
        "-ho", "OBSERVER/AGENCY",  # observer and agency
        "-hr", "UBX_RECEIVER/UBLOX/V1.0",  # receiver number, type, version
        "-ha", "ANT001/UBLOX_ANTENNA",  # antenna number and type
        "-hp", "0.0000/0.0000/0.0000",  # approximate position XYZ (meters)
        "-hd", "0.0000/0.0000/0.0000",  # antenna delta H/E/N (meters)
        "-hc", "Converted from UBX files using RTKLIB convbin",  # comment
        "-hc", "For OPUS and GNSS post-processing"  # additional comment
    ]
    try:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            print(f"Warning: convbin exited with code {result.returncode}")
    except Exception as e:
        print(f"Error running convbin: {e}")
        sys.exit(1)


def run_convbin_with_headers(combined, out_obs, out_nav, args):
    cmd = [
        "convbin", combined,
        "-r", "ubx",
        "-o", out_obs,
        "-n", out_nav,
        "-f", "3",  # dual-frequency L1/L2
        "-v", "3.04",  # RINEX version 3.04
        "-hm", args.marker_name,
        "-hn", args.marker_number,
        "-ht", "GEODETIC",
        "-ho", args.observer,
        "-hr", args.receiver,
        "-ha", args.antenna,
        "-hp", "0.0000/0.0000/0.0000",
        "-hd", "0.0000/0.0000/0.0000",
        "-hc", "Converted from UBX files using RTKLIB convbin",
        "-hc", "For OPUS and GNSS post-processing"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            print(f"Warning: convbin exited with code {result.returncode}")
    except Exception as e:
        print(f"Error running convbin: {e}")
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(
        description="Combine UBX files in a directory and convert to RINEX for OPUS (cross-platform)"
    )
    p.add_argument("input_dir",
                   help="Directory containing .ubx files (in time order by filename)")
    p.add_argument("-o", "--outdir", default="rinex_out",
                   help="Directory to write RINEX files into")
    p.add_argument("--marker-name", default="UBX_STATION",
                   help="Marker name for RINEX header")
    p.add_argument("--marker-number", default="001",
                   help="Marker number for RINEX header")
    p.add_argument("--receiver", default="UBX_RECEIVER/UBLOX/V1.0",
                   help="Receiver number/type/version for RINEX header")
    p.add_argument("--antenna", default="ANT001/UBLOX_ANTENNA",
                   help="Antenna number/type for RINEX header")
    p.add_argument("--observer", default="OBSERVER/AGENCY",
                   help="Observer name and agency for RINEX header")
    args = p.parse_args()

    if not os.path.isdir(args.input_dir):
        sys.exit(f"Error: '{args.input_dir}' is not a directory.")

    # gather .ubx files sorted by name
    ubx_files = sorted(
        os.path.join(args.input_dir, f)
        for f in os.listdir(args.input_dir)
        if f.lower().endswith('.ubx')
    )
    if not ubx_files:
        sys.exit(f"Error: no .ubx files found in '{args.input_dir}'.")

    os.makedirs(args.outdir, exist_ok=True)
    combined = os.path.join(args.outdir, "combined.ubx")
    print(f"▶︎ Combining {len(ubx_files)} files into {combined}")
    combine_ubx(ubx_files, combined)

    convbin = find_tool(["convbin", "convbin.exe"])
    if not convbin:
        sys.exit("Error: 'convbin' not found in PATH. Please install RTKLIB tools and ensure convbin is in your PATH.")

    obs = os.path.join(args.outdir, "output.obs")
    nav = os.path.join(args.outdir, "output.nav")
    print("▶︎ Using RTKLIB convbin to produce dual-frequency RINEX")
    run_convbin_with_headers(combined, obs, nav, args)
    print(f"✔︎ Wrote observation file: {obs}")
    print(f"✔︎ Wrote navigation file:  {nav}")

    # Check if files have data
    for f in [obs, nav]:
        try:
            with open(f, 'r') as fh:
                lines = fh.readlines()
                if len(lines) <= 20:
                    print(f"⚠️  Warning: {f} contains only header or very little data.")
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    main()
