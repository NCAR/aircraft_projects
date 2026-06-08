# Changelog

Changelog for the camera scripts in `aircraft_projects/scripts/camera/`

## [2.0] - 2026-06-08

### Fixed
- `combineCameras.pl`:
  -  Generalize RAW_DATA_DIR to read from env so can run on gs3 (/var/r1) or servers (/scr/raf/Raw_Data)
  - Accept CAMERA or camera as dir name - we have developed some inconsistencies here
- `createMovies.sh`: Fix bug in how directions were cycled through. Add checks for existence of needed env vars

### Added
- `combineCameras.pl`:
  - Untar image dir if not already done.
- `createMovies.sh`: Add ability to override $PROJECT on the command line
- git ignore generated movieParamFile and movieParamFile.bak files in the proj/platform/scripts dir.

## History (pre-2.0)

Earlier change history for `combineCameras.pl` (Stuart Beaton, NCAR/RAF),
moved here from the script header. Contributor initials: SB = Stuart Beaton,
JAG/JAA = Janine Aquino, TMT = Taylor Thomas, CBS = Brooks Snyder.

### 2018-03-13 — TMT
- Added argument to two pass MPEG encoding to enable previewing in ZINC.

### 2012-05-01 — JAA, CBS
- Added option to overlay imagePointing on each camera image.

### 2012-04-26 — JAA
- Upgrade to handle 4 images for TORERO.

### 2012-02-22 — JAA
- Handle case where images don't start until after midnight.

### 2012-02-10 — JAA
- Add new param movieDirectory to specify where to output movies.

### 2012-01-18 — JAA (= JAG)
- If data is missing, continue on without including data.

### 2010-10-01 — JAG
- Code sometimes dies mid processing. If startNum given on command line,
  recover by starting there.

### 2010-09-23 — JAG
- Movie Date and Time range was only being calculated from netCDF file if
  netCDF data was included. Add ability to calc date/time from image filenames.

### 2010-06-21 — JAG
- Move outputWidth to keywords (was hardcoded) so that if data is too wide and
  overwrites labels, it can be fixed in config file.
- Change data image height to pull from outputResolution, not scale, so data
  can be taller than image if necessary to accommodate PI var request list.
- Bug in enddate extraction added Jun 17: both end month and end minute were
  `emn` — fixed.

### 2010-06-17 — JAG
- Added ability to increment enddate extracted from .nc global vals if flight
  rolls over midnight.

### 2010-01-26 — JAG
- Added more comments. Streamlined code and moved some code to subroutines.
- Generalized to support many different camera configuration/number of cameras.

### 2006-08-23 — SB
- Added `$cameraName` and image adjustment keywords.
- Added default scale, outputResolution, and bit rate for axis camera.
