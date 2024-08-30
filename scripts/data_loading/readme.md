# Data Loading Readme

_!!! The data loading workflow still relies on scripts that are located in subversion to load the datasets into CODIAC and DTS. This script just sets up the yaml files for insertion, and reads the SQL database values to perform basic checks on its contents !!!_

## YAML: Base Configuration Files and Templates

The templates for the datasets are broken up into the `base_config` directory, the `templates` directory, and then the project specific `project_template.yml`. 

 ### Base Dataset Configuration

The dataset specific `.yml` files life in the `base_config` directory which specify the format, author, summary, xlink, and any other dataset specific information. Fields that will be filled in by the `replace_yaml.py` script are enclosed in brackets (e.g. `<PROJECT>` or `<aircraft>`). 

If datasets have similar structures but need different descriptions or filenames, the base configuration files will produce multiple dataset configurations. In this case, the yaml file has a `dataset_cfg` section that provides the base template for all of the datasets produced by that file that is passed 

### Templates

The templates folder has the base aircraft templates to fill in based on the aircraft flown for the project. Each template contains all the aircraft specific configuration variables.

### Project Template

The configuration version of the `project_template.yml` is located in `$PROJ_DIR/Configuration/scripts/` and a new one will be created for each project. This will contain the specific archive IDs for each dataset, the area and time bounds, project-wide xlinks, and the standard, shared database fields.

The project template has eight sections:
 1. variables: Key-value pairs to fill in brackets within the configuration files like `<project>`, or `<year>`
 2. fields: Project specific fields like start and end date, and lat and lon range.
 3. archive_ids: Two values for each key: [id, version_number]. The ID corresponds to the Field Data Archive ID number, and version number is the current version to be loaded. If either is empty the config file will not be created. The `base_config` file must have the corresponding key value in brackets in the `archive_id` spot for the script to fill it in correctly (e.g. for an ADS `base_config` yml it would look like `archive_id: <ads>`)
 4. dts: DTS specific fields to be filled in for all datasets
 5. codiac: FDA specific fields to be filled in for all datasets
 6. preliminary: Fields that will be added to yaml if dataset is preliminary (version_number < 1.0)
 7. final: Fields that will be added to yaml if dataset is final
 8. paths: Archive and ingest path bases to be filled in based on dataset quality.

##  replace_yaml.py

Usage: `python replace_yaml.py <PROJECT>` 
The replace yaml file pulls all of these templates together based on the project and aircraft and saves the configuration files that have an assigne archive_id into the `/net/work/cfg-files/` directory for the specific project.

 1. Checks the FDA and DTS fields in the project_template and prints the key-value pairs of what will be replaced using the results from `_database_fields.py`
 2. Iterates through base_config directory and checks if archive_id exists for each dataset; continues if it does not
 3. Checks that a version number exists and adds it. If version is less than 1.0, adds in preliminary fields, otherwise adds in final fields.
 4. Adds in ingest and archive paths based on version number if they do not already exist in the dataset.
 5. Append project x_links to dataset specific x_links (if they exist)
 6. Replace variables in brackets.
 7. Add in fields from templates. If field already exists in dataset prompt the user to reject or accept the change.
 8. Saves the configuration file in the `/net/work/cfg-files/` directory for the specific project.

### _database_fields.py

This script connects with the SQL database (using `_mysql_connect.py`) to ensure that the correct fields are being filled into the config files. It fills out the `_zith9.py` template with the SQL values and then is read in by `replace_yaml.py`













