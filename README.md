# UBX to RINEX Conversion for GNSS Post-Processing for OPUS

This workflow allows you to combine multiple u-blox UBX files and convert them to standard RINEX files suitable for OPUS and other GNSS point positioning services. It is cross-platform and works on both Linux and Windows.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
  - [1. Install Python 3](#1-install-python-3)
  - [2. Build RTKLIB 2.4.3 (convbin)](#2-build-rtklib-243-convbin)
  - [3. Install convbin](#3-install-convbin)
- [Usage](#usage)
- [Advanced Options](#advanced-options)
- [Troubleshooting](#troubleshooting)
- [References](#references)

---

## Features
- Combines all `.ubx` files in a directory (sorted by name) into a single file
- Converts the combined UBX file to RINEX observation (`.obs`) and navigation (`.nav`) files
- Produces RINEX files compatible with OPUS and other GNSS post-processing services
- Cross-platform: works on Linux and Windows
- Robust error handling and clear status messages

---

## Requirements
- **Python 3** (tested with 3.8+)
- **RTKLIB 2.4.3** (specifically the `convbin` tool, built from source)
- u-blox UBX files containing raw measurement messages (`RXM-RAWX`, `RXM-SFRBX`, etc.)

---

## Setup

### 1. Install Python 3
- On macOS: `brew install python`
- On Ubuntu: `sudo apt-get install python3`
- On Windows: [Download Python](https://www.python.org/downloads/)

### 2. Build RTKLIB 2.4.3 (convbin)

#### Clone the correct RTKLIB version:
```sh
git clone -b rtklib_2.4.3 https://github.com/tomojitakasu/RTKLIB.git
```

#### Build convbin (macOS/Linux):
```sh
cd RTKLIB/app/consapp/convbin/gcc
# Edit the makefile:
# - Remove the '-ansi' flag from CFLAGS
# - Remove '-lrt' from LDLIBS (macOS only)
make clean && make
```

#### On Windows:
- Use the Visual Studio project in `RTKLIB/app/consapp/convbin/msvc` or use MinGW to build.
- Or download a pre-built binary from the [RTKLIB releases page](https://github.com/tomojitakasu/RTKLIB/releases).

### 3. Install convbin
Copy the built `convbin` executable to a directory in your PATH, e.g.:
```sh
sudo cp convbin /usr/local/bin/
```
Or add the build directory to your PATH.

---

## Usage

1. **Place all your `.ubx` files in a directory.**
2. **Run the script:**
   ```sh
   python3 ubx2rinex.py /path/to/your/ubx_directory
   ```
   - Output will be in the `rinex_out/` directory by default.
   - You will get:
     - `rinex_out/combined.ubx` (all UBX files stitched together)
     - `rinex_out/output.obs` (RINEX observation file)
     - `rinex_out/output.nav` (RINEX navigation file)

3. **Upload the `.obs` and `.nav` files to OPUS or your GNSS processing service.**

#### Optional: Specify a different output directory
```sh
python3 ubx2rinex.py /path/to/ubx_dir -o my_rinex_dir
```

#### Customize RINEX Headers (Recommended for OPUS)
To eliminate OPUS warnings about missing antenna information, specify your actual equipment:

```sh
python3 ubx2rinex.py /path/to/ubx_dir \
  --marker-name "MY_STATION" \
  --marker-number "001" \
  --receiver "REC001/ZED-F9P/V1.0" \
  --antenna "ANT001/UBLOX_ANTENNA" \
  --observer "YOUR_NAME/YOUR_AGENCY"
```

**Important**: Use your actual antenna type (e.g., `ZED-F9P-01A` for u-blox ZED-F9P) to ensure proper phase center corrections in OPUS.

---

## Advanced Options
- You can customize the RINEX header (marker name, receiver, antenna, etc.) by editing the `run_convbin` function in `ubx2rinex.py` and adding options like `-hm`, `-hr`, `-ha`, etc. See the RTKLIB documentation for details.
- To process only a subset of files, move/copy them to a separate directory before running the script.

---

## Troubleshooting

### No Data in Output Files
- Ensure your UBX files contain raw measurement messages (`RXM-RAWX`, `RXM-SFRBX`).
- Use `convbin -r ubx -scan yourfile.ubx` to check for observation messages (O=... in the output).
- If you see only headers in `.obs`/`.nav`, your UBX files do not contain the required data.
- Make sure you are using the correct version of `convbin` (RTKLIB 2.4.3 or newer).

### convbin Not Found
- Ensure `convbin` is in your PATH. Try `which convbin` (Linux/macOS) or `where convbin` (Windows).

### Build Errors (macOS)
- Remove `-ansi` from `CFLAGS` and `-lrt` from `LDLIBS` in the Makefile.

---

## References
- [RTKLIB Official Repository](https://github.com/tomojitakasu/RTKLIB)
- [RTKLIB Manual (PDF)](https://rtklib.com/prog/manual_2.4.3.pdf)
- [OPUS (Online Positioning User Service)](https://geodesy.noaa.gov/OPUS/)
- [u-blox Documentation](https://www.u-blox.com/en/docs)

---