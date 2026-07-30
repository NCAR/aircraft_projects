# Changelog

Changelog for the camera scripts in `aircraft_projects/scripts/camera/`

## [2.2] - 2026-07-30

### Updated
- `combineCameras.pl`: Frames are no longer driven by the images in `imageDir1`. All
  image directories are scanned, and a frame is created every `$FRAME_INTERVAL` (1)
  second from the earliest to the latest image time found in ANY of them. Previously a
  second with no `imageDir1` image produced no frame at all, even when the other
  cameras had images - with cameras working intermittently, that dropped most of the
  flight.
- `combineCameras.pl`: A camera with no image at a frame time reuses its previous
  image, as long as that image is no more than `$TIME_TOLERANCE` (5) seconds old. This
  covers cameras recording every few seconds and short dropouts. Past the tolerance the
  camera contributes a blank tile rather than a stale image. The time overlay shows the
  time of the image itself, so a carried-forward image is apparent.
- `combineCameras.pl`: Frame times are handled in seconds rather than as `HHMMSS`
  strings, so a flight crossing UTC midnight stays in order.
- `combineCameras.pl`: `camera`/`CAMERA` resolution and untarring now run once per
  directory, for all directories, instead of once per directory per image and only for
  `imageDir1`. A camera directory that doesn't exist is reported and left blank rather
  than killing the run.
- `combineCameras.pl`: All frame-timing constants (`$FRAME_INTERVAL`,
  `$TIME_TOLERANCE`, `$IMAGE_NAME_PATTERN`, `$MISSING_IMAGE_COLOR`) are together in the
  hardcoded values section at the top of the script.
- `README.md`, `movieParamFile.template`: Note that frame times come from all image
  dirs, not `imageDir1`.

### Fixed
- `combineCameras.pl`: An image filename that didn't match the expected
  `*YYMMDD-HHMMSS.jpg` pattern used to exit the whole script; such files are now
  ignored. The pattern accepts `-` or `_` between date and time and an optional
  pointing suffix (`260729-120000_d.jpg`), replacing the sequence of filename guesses
  that used to be made per image.
- `combineCameras.pl`: The blank tile used for a missing image is now sized to the
  camera `scale` instead of relying on the forced scale to resize a default canvas.
- `combineCameras.pl`: The movie start time in the output filename is taken from the
  first frame, so it is still correct when restarting mid-flight with `startnum`.

## [2.1] - 2026-07-28

### Added
- `createMovies.sh`: If no camera image directions are found for a flight, look for a
  `flight_number_<flight>.tar` tarfile next to the flight directories, extract it in
  place, and check for the directions again. Images often come off the aircraft still
  packed by `scripts/copy_images.sh`.
- `test/testCreateMovies.sh`: New tests for camera directory resolution - unpacked
  flight dirs, tarfile extraction, a tarfile that won't extract, and flights with no
  images. Builds its own scratch fixture tree, so no project data is needed.

### Updated
- `createMovies.sh`: Skip a flight that still has no image directions after the tarfile
  check, instead of writing a param file and running `combineCameras.pl` with nothing to
  process. Remaining flights on the command line are still processed.
- Pulled the direction scan into a `scan_camera_dirs` function so it can be re-run after
  extracting a tarfile.

## [2.0] - 2026-06-08

### Fixed
- `combineCameras.pl`:
  -  Generalize RAW_DATA_DIR to read from env so can run on gs3 (/var/r1) or servers (/scr/raf/Raw_Data)
  - Accept CAMERA or camera as dir name - we have developed some inconsistencies here
- `createMovies.sh`: Fix bug in how directions were cycled through. Add checks for existence of needed env vars

### Updated
- Changed movieParamFile to be per-flight so can make per-flight updates. During TI3GER-2, two cameras were not
  working for a flight, so this will allow that flight to only display those two cameras. 
- Add ability to run script to generate per-flight file, then exit, edit and finally run with edited file.

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
