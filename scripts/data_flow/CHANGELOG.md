# Changelog

Changelog for the data flow scripts in `aircraft_projects/scripts/data_flow/` —
`push_data.py`, `sync_field_data.py`, their supporting `_*.py` modules, and the
`test/` suite.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/).
Version numbers are coarse groupings of related work rather than tagged releases;
each section also lists the date (range) of the changes it covers.

## [3.6] - 2026-06-01

### Fixed

- `_process.py`: `_extract_date_from_ads_filename` set `self.date` internally but
  returned `None`, and all five callers in `extract_takeoff_lrt` assigned that
  return value back to `self.date` — so any flight whose date fell back to the ADS
  filename ended up with `date = None`. The method now returns the date, matching
  its docstring.
- `test/test_push_data.py`: patch `Process.extract_takeoff_lrt` with
  `autospec=True` so the mock is bound and `self` is passed to the side effect.
- `test/test_sync_field_data.py`: `test_ingest_to_local` now mocks `os.path.exists`
  (so the source's missing-source-dir guard is satisfied) and `create_directory`
  (so the `PMS2D` branch doesn't create a real directory during the test).

### Changed

- Relaxed the documented Python requirement from 3.12 to 3.9 (3.9 is installed on
  gs3 and runs both the scripts and the tests). Updated `readme.md`, `run_tests.sh`,
  and `test/testenv.yml` (`python ==3.12` → `python >=3.9`).
- Clarified the deployment section of `readme.md`.

## [3.5] - 2026-04 – 2026-05

### Added

- Camera distribution from FTP in `sync_field_data.py`.
- Updated field data processing steps and merged relevant content from the
  RAFGroundstation wiki into `readme.md`.

### Fixed

- `find_file` error that blocked reprocessing.
- ICARTT file lookup now matches on date only, avoiding misses caused by
  inconsistent filename naming conventions.
- Path-creation error in `sync_field_data.py` (assign a single value from the
  returned tuple).

### Changed

- Removed ship status when using SyncThing, since syncing happens asynchronously.

## [3.4] - 2025-08

### Changed

- Reworked ICARTT date handling to use the `flt_time` command for takeoff time,
  with more robust error handling when extraction fails.
- `push_data.py` now stores the ICARTT filename when it generates the file.
- General ICARTT file-handling cleanup.

## [3.3] - 2025-07

### Added

- GOTHAAM project data flow support.
- SATCOM log syncing to the raw data directory when available.
- Camera image syncing in the data flow.

### Changed

- Data flow reads the `nc2asc` batch file (later iterated on; batch-file command
  for `nc2asc` adjusted).
- PMS2D processing uses the last ADS file when multiple ADS files exist.

### Fixed

- Value-error when unpacking the return of `find_file`.
- PMS2D syncing and assorted file-path fixes for syncing.
- Typos in the data flow.

## [3.2] - 2025-05

### Added

- IWG1 data to the CGWAVES transfer; when multiple ADS files are found for one
  flight, the files are listed and the user is prompted before using the first.
- Ship all ADS files for a flight even when only the first is processed.

### Changed

- Updated default email recipients and added a note about the HTTPS site in the
  status email.

### Fixed

- `.shtml` files are now ignored when syncing.
- `data_dir` was overwriting `raw_data_dir`; ADS files syncing to `data_dir`.
- Corrected `field_sync` paths and local-distribution-from-FTP paths.

## [3.1] - 2024-09 – 2024-12

### Added

- SyncThing data process and staging (`_syncThing.py` / `StageSyncThing`),
  enabling peer-to-peer sync back to Boulder.

### Changed

- Updated directory naming in the sync field data scripts.

## [3.0] - 2024-06 – 2024-07 — Modular refactor

### Changed

- Split the monolithic `push_data.py` into focused modules: `_setup.py` (Setup),
  `_process.py` (Process), `_NAS.py` (DataShipping), `_FTP.py` (TransferFTP),
  `_zip.py` (SetupZip), `_GDrive.py` (GDrive), `_findfiles.py` (FindFiles), and
  `_logging.py` (MyLogger). The `test/` suite was reworked to match.

### Added

- `check_env.py` to validate required environment variables before imports.
- Multi-email functionality with adapted tests.
- `test/testenv.yml` and a test readme; per-developer test environment setup.

### Fixed

- Catch `SystemExit` so macOS doesn't throw an exception.
- Hard-coded path errors in tests; tests now read paths from environment variables.

## [2.1] - 2024-01-29 — Consolidation

### Changed

- Moved all data flow scripts and Python unit tests into a single
  `scripts/data_flow/` directory in preparation for the modular refactor.
- Switched tests to use environment variables (`PROJ_DIR`, etc.) to set paths.

## [2.0] - 2022-09-14

### Fixed

- Refactor of program from procedural to object-oriented, with all functions
  defined within class FieldData.
- Main function contains high-level conditionals based on project configuration.
- flake8 cleanup.

### Added

- /test subdir containing set of tests for functions within FieldData class
  defined in push_data.py.
- function setup_GCP, which will be called during MAIR-E project to transfer data
  to the MethaneSAT Google Cloud Platform Bucket.
