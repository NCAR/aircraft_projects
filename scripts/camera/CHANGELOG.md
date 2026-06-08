# Changelog

Changelog for the camera scripts in `aircraft_projects/scripts/camera/`

## [2.0] - 2026-06-08

### Fixed
- Generalize RAW_DATA_DIR to read from env so can run on gs3 (/var/r1) or servers (/scr/raf/Raw_Data)
- Accept CAMERA or camera as dir name - we have developed some inconsistencies here

### Added
- Untar image dir if not already done.
