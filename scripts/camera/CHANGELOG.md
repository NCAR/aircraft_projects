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
