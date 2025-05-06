# LRT_archiving Folder

The `LRT_archiving` folder contains scripts and files for archiving LRT netcdf files during the CAESAR C130 N130AR project. Below is a description of the files in this folder:

## Files

- **merge_WVISO**: A Python script to merge netcdf files containing WVISO data with aircraft data.
- **update_metadata.sh**: A Bash script to add missing metadata to the merged files.
- **merge**: A Bash script that:
    - Converts chemistry ICARTT files to netcdf.
    - Merges aircraft data with chemistry data using `ncmerge`.
    - Merges the result with WVISO data using the `merge_WVISO` script.
    - Runs `update_metadata.sh` to add missing metadata.
    - Removes preliminary variables using `ncks`.