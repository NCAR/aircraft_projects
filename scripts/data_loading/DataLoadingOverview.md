# Data Loading Overview

The EOL data policy states "At the conclusion of each field campaign, EOL will provide access to the initial set of preliminary EOL data via a centralized, password protected location.", so before the field data storage is taken down, the data need to be loaded into the FDA, password protected, and made available to the team.

The first, time-critical step is to make sure you obtain a copy of all the necessary data before the field phase ends. After that, archiving EOL data requires two additional steps. The first, setting up the archive environment, need only be done once. The second, loading a dataset, needs to be done for each dataset that is being archived.

## 1. Make sure you have access to all the data

- If Google Drive, ftp, or syncthing were used for field data storage, turn off syncing between the staging directory and local disk
  - `ssh -AY ads@eol-rosetta.eol.ucar.edu`
  - `crontab -e`
  - Comment out the relevant rclone and sync_field_data.

  ```bash
  # Get data from Google Drive to local ingest point
  */5 * * * * . /h/eol/ads/.bashrc && rclone copy gdrive_eolfield:$PROJECT $RAW_DATA_DIR/$PROJECT/field_sync --ignore-existing > /tmp/sync.log 2>&1
  # Distribute from local ingest point to data dirs
  */5 * * * * . /h/eol/ads/.bashrc && $PROJ_DIR/scripts/data_flow/sync_field_data.py > /tmp/sync.log 2>&1

  ```
- If using rclone, be sure to turn off syncing from the ground station as well

- Before the field data storage is taken down, be sure that all field-phase data have been copied back to EOL servers and that you know where they are. This applies not only to RAF datasets, but to PI preliminary field-phase data.
  - For PI data, send DMS an email enumerating the data that needs to be loaded and ask them to take care of it.
  - For RAF datasets, continue to step 2.

## 2. Set up the dataset archive environment

1. Confirm that the EOL project page exists (`https://www.eol.ucar.edu/field_projects/<project>`). If not, create it. The RAF Project Managers (PMs) generally create this page before the project, so if you have questions, determine who is the PM for this project and ask them.
2. Check if the project exists in the FDA. Go to <https://data.eol.ucar.edu/> and search for the project. If it does not exist, then you likely need to create the project page, as well as the DTS dataset page.
3. Add the EOL Project homepage as an xlink to the project page in the FDA.
4. Add a link from the EOL project page to the FDA project page to the Data Access right navigation block.

## 3. Archive a dataset

For each field project in which RAF is involved, the following data is generally created during the field phase: ADS files, camera images, preliminary LRT data, preliminary KML data, PMS2D data. Optionally, HRT and SRT data are also created. Any data that is archived as preliminary should have a final version created, so ensure that data will be quality controlled before archiving. If a preliminary dataset is archived and later a final version is not created, that dataset can be hidden after the project data becomes public.

> A note on authorship: Individuals can be authors where appropriate, such as Julie for the MTP. When a group of individuals are involved, then a team can be a dataset author, such as the Digital Camera Imagery team. The publisher should always be EOL and the primary point of contact should always be EOL Data Support.

For more information on the load data scripts located in `/net/work/bin/scripts/insert`refer to the loaddata documentation and repository (previously in SVN) for more details: [User Documentation](https://docs.google.com/document/d/1aVVNo_54ndl3DpHomTE-fZMALAKPYwPzgEWlYkvJC-s/edit?tab=t.0#heading=h.alm7n6amq6xt) and [Github Repository](https://github.com/NCAR/eol-svn-repository/tree/main/tools/database/insert_scripts/trunk)

**Dataset-specific notes:**

- For the ADS data, archive the RF, FF, TF, and CF files. Hangar flights, other than the CF files, do NOT need to be archived unless requested.

For each of these datasets, perform the following steps to add the data to the archive. Unless otherwise noted, run them as yourself:

1. If not there already, copy the ads, camera, PMS2D and other raw data files to `/scr/raf/Raw_Data/<project>`. Copy all data that receives processing (LRT, HRT, SRT, KML, etc) to `/scr/raf/Prod_data/<project>`. The files in `/scr/raf_data`, `/scr/raf/local_productiondata` and individual PMs ftp areas are subject to being overwritten. By copying the files here, it is possible to cleanly keep track of file versions. Files should be put into subdirectories by version number.

**A note on versioning:**
Versioning should be handled as follows:
| Data phase | Version number |
| --- | --- |
| 0.1, 0.2, ... | Field phase data |
| 0.9 | Last in-house version (contains all variables) from /scr/raf_data dir. Files will be owned by an individual employee |
| 1.0, 1.1, etc | Final data run as user nimbus from /scr/raf/local_productiondata |

2. Copy the data to Campaign Storage or local archive location, depending on data type.
   - All data that is not netCDF data needs to be loaded to Campaign Storage as user `eoldata` / group `eoldmg`.
   - netCDF data should be archived to `/net/archive/data`, so that the files can be made available via OPeNDAP. This is done by checking the Dodsable box in the FDA (which is configured to happen automatically when using the scripts below). Preliminary files are not to be made available via OPeNDAP, but it is cleaner to keep all versions of a dataset in the same archive location (DOES NOT CURRENTLY WORK, but still archive netcdf here)

3. Change directories to `/net/jlocal/projects/<project>/<aircraft>/Production`. Confirm that the archive dir exists. If not, copy it from a recent project. `cd` to the archive dir.

4. Edit `archAC.sh` and set `PROJECT`, `YEAR`, `PLATFORM`, and `EMAIL` near the top of the file. Uncomment the line for the data you are working with, and make sure all other lines are commented out, except the variable assignments. Save your changes.

5. Run `./archAC.sh`. The script calls `archAC.py` which automatically computes sha256 checksums for each file before transfer, rsyncs the files to the archive, then verifies the checksums on the archive server and reports a match or mismatch per file. Results are written to `checksums.txt` in the archive location. If a mismatch is reported, re-copy the affected files and re-run.

6. Generate the dataset YAML config files and load to the FDA and the DTS
   - See [readme.md](readme.md) for setup requirements. **Don't skip this step! The code will fail if your environment is not configured correctly**
   - Copy `project_template.yml` from `$PROJ_DIR/Configuration/scripts/project_template.yml` to `$PROJ_DIR/<PROJECT>/<aircraft>/scripts/project_template.yml`.
   - Edit `project_template.yml`. There are blocks separated by comment lines.
     - In the variables block:
       - Replace 'PROJECT' with the project name in upper case, and 'project' with it in lower case.
       - Add the aircraft and year. The year must be in single quotes, eg '2026'.
     - In the fields block:
       - Update the project dates and add the lat/lon in single quotes
     - In the archive_ids block:
       - Add the dataset id and version number for each dataset for which you want to create a YAML file
     - Update the internal_contact_id_dts, load_contact_id_dts, and author_id_dts to be your DTS id. You can find your contactID by logging in to the DTS and looking at the URL for your entry on the Add/Edit Users page
     - Update the internal_contact_id_codiac to be your CODIAC id. To find your internal contact ID, login to data.eol.ucar.edu, switch to editor mode, go to Contact List, search for your name and find your id in the URL of your entry.
   - From the `scripts/data_loading/` directory, run `python3 replace_yaml.py <PROJECT>`. This script reads the `project_template.yml` for the project and all base config templates, automatically substitutes all variables (e.g. `<PROJECT>`, `<year>`, archive IDs), and saves the generated YAML files to `$CFG_FILES_DIR/<PROJECT>*/` (default: `/net/work/cfg-files/<PROJECT>*/`).
   - Now `cd /net/work/bin/scripts/insert/loaddata` and run `./load_a_dataset.pl`, giving the full path to each yml file generated above. This script will create an FDA dataset, create a DTS entry, and add all the data files to the new dataset. Hit return when prompted. When the script completes, it will prompt you to perform additional tasks by hand. (These would all be great areas to automate in the future.)

7. Run `/net/work/bin/emdac/lsdsfiles -lv <archive_ident>` on datasets with files archived locally to `/net/archive` (`lsdsfiles` does not work with files on campaign storage)
   - `lsdsfiles` is a script that performs a set of sanity checks on a dataset and can help identify common errors.
   - To see the usage statement, run `perldoc lsdsfiles`

8. Check and test order the dataset by hand.

9. For all data except ADS files, make it visible in the FDA, then add it to the Master List.

10. Currently, the scripts are not able to add all the required metadata. That functionality will be added as we can, but in the meantime the following items need to be added by hand through the GUI.
    - Add an FDA user and a EULA file for these preliminary (restricted) datasets. Do not assign a DOI for preliminary datasets.
    - Add links to documentation as xlinks — be sure to add the EOL Project Homepage and aircraft Documentation Summary page to the dataset. You can also add a link to the missions table in the field catalog.
    - When you receive the Project Managers Data Quality Report, add it as a related `link:info`
    - If loading browseable files, such as camera movies, hand add browse_extract program (sti).
    - For camera movies, set FDA Plot Type as `static_image` to avoid default playback image.
    - For the camera imagery datasets, make the other camera datasets companions using the `related link:companion` function.
    - Add GCMD science keywords — use a recent past-project to get an idea of what to add. The YAML files offer the base GCMD keywords needed for a project, but for more complex air chemistry, cloud physics etc, additional keywords need to be added. (#TODO: Create automated keyword additions based on file contents)
    - For netCDF files, add a link to the aircraft_nc_utils repo and the NCAR-RAF netCDF conventions webpage
    - For oap data add links to the appropriate xpms2d pages.
    - *(As other datasets with specific links come to light, add them here. We can use this as a reference for updating the script to do this automatically.)*

11. Update DTS to inform Janine that the new version is ready to be checked. It is a best practice to have a second set of eyes take a look at anything that "goes out the door" (is available to the public), so please have someone familiar with data loading take a look at every dataset.

12. Once checked, update the DTS (<http://dmg.eol.ucar.edu/dts/dln/>) for your dataset and mark it done.

13. Return to step 1 for the next dataset.

---

**You are done archiving a new dataset.**

---

## To add a set of files for a new version to an existing dataset

1. Update DTS and assign yourself the dataset to change. Assign Janine as the checker.

2. Copy the files from the ingest location to the archive location.

3. `cd /net/jlocal/projects/<PROJECT>/<AIRCRAFT>/Production/archive`
   Note the aircraft that flew for this project. You will need that info in the next step.

4. Edit `archAC.sh`
   - Comment out all existing uncommented lines.
   - Create a new line for the data you want to load.
   - Log in as user `eoldata`
   - Run `./archAC.sh`

5. Go to the dataset in the FDA and hide all the files in the existing version.
   - If you are loading final data, uncheck "Eula Reqd" on the main "Edit Dataset" page for the dataset.
   - Click on Version on the left, then do a bulk update to hide the files. Also hide the EULA, if it exists, so that it will stay with the preliminary data.

6. Create a new version with the version number you want. **See the note on versioning above.** Be careful not to add the just-hidden files to the new version. Keep this window open so you can refer to it in step 4.

7. If you are moving from a preliminary to final version of the data, update the description in the FDA to match your new `.yml` file. The version number change handled by `update_version.py` in the next step will automatically set the quality from preliminary to final.

8. Update the dataset YAML config manually or with `update_version.py` and add new files to the FDA using `insert_multiple_files`.
   - `cd /net/work/cfg-files/<PROJECT>`
   - Update the version (and optionally ingest location or filename pattern) in the existing `.yml` file by running `update_version.py` from the `scripts/data_loading/` directory:
     `python3 update_version.py <PROJECT> <DATASET> --version 1.0 [--ingest /new/path] [--pattern new_pattern]`
   - If there is no existing `.yml` file, generate one by running `python3 replace_yaml.py <PROJECT>` from `scripts/data_loading/` as described in step 7 above.
   - Log in as user `eoldata`
   - Run `./insert_multiple_files -u <YOUR_USERNAME> XXX.yml` (from `/net/work/bin/scripts/insert/`)
   - Run `/net/work/bin/emdac/lsdsfiles -lv ###.###` to check dataset if data files are archived locally to `/net/archive` (does not work with campaign storage)
   - Test order dataset

9. Go back to the FDA, under the version tab and confirm the new files are under the new version.

10. Update DTS to inform Janine (for now) that the new version is ready to be checked.

11. Go to the Master List Editor and edit the listing for the file — update as required, check "updated", and save to get an updated date. (deprecated -- no more master list after CAESAR, 2024)

12. Once checked, update the DTS (<http://dmg.eol.ucar.edu/dts/dln/>) for your dataset and mark it done.

13. Run `whods <archive_ident>` (e.g. `whods 87.050`) to get a list of email addresses of people who have ordered the data and the date they ordered it. Send an email to all these folks letting them know the data have been updated, the changes that were made, and where they can download the updated data. Alternatively, look at 'Stats' on the FDA.

---

**You are done updating an existing dataset with a new version.**

---

## Updating load_data_proj and other insert scripts

Occasionally you will need to update the template yaml files, or even less frequently the scripts, in `/net/work/bin/scripts/insert`. **Do not make changes to that dir.** Follow the instructions in the README file to check out your own copy of the repository, make changes, and deploy to the production.
