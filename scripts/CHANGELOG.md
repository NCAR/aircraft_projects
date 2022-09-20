# Changelog

Changelog for push_data.py within aircraft_projects/scripts.

## [2.0] - 2022-09-14

### Fixed

- Refactor of program from procedural to object-oriented, with all functions defined within class FieldData. 
- Main function contains high-level conditionals based on project configuration. 
- flake8 cleanup.

### Added

- /test subdir containing set of tests for functions within FieldData class defined in push_data.py. 
- function setup_GCP, which will be called during MAIR-E project to transfer data to the MethaneSAT Google Cloud Platform Bucket. 
