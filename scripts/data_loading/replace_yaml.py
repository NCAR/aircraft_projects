#!/usr/bin/env python
import os
import sys
import re
import glob
import yaml # type: ignore
from collections import OrderedDict
from _database_fields import FieldsCheck
project_folder = os.environ['PROJ_DIR'] + '/' + os.environ['PROJECT'] + '/' + os.environ['AIRCRAFT'] + '/scripts'
base = os.environ['PROJ_DIR'] + '/scripts/data_loading'
global_fields = ['fields', 'dts', 'codiac', 'paths', 'standard'] 

def check_template(t_path,search, check):
    with open(t_path) as f:
        template = yaml.safe_load(f)
    for group in ['dts','codiac']:
        for field in template[group]:
            if field=='xlink_id':
                #print(check[field])
                print(f'Appending the following xlinks: {template[group][field]}')
                continue
            try:
                value = int(template[group][field]) #Value in the cfg file
            except ValueError:
                value = template[group][field]
                print(f'The template is set to replace the {field} field with {value}')
                continue
            key = find_key_by_value(search, field)  ##Find the grouping in the zith9dict that the field is in      
            #print(f'key:{key}, and value:{value}')
            #print(check[key])
            database_val = check[key][value]
            print(f'The template is set to replace the {field} field with {database_val}')
        
def find_key_by_value(search_dict, field):
    for key, values in search_dict.items():
        if field in values:
            return key
    return field 

def replace_variables(replace, value):
    """
    Finds and replaces variables in <> with their corresponding values in the replace dictionary.
    Parameters:
    replace (dict): A dictionary containing variable-value pairs.
    value (str): The string in which variables need to be replaced.
    Returns:
    str: The modified string with variables replaced by their corresponding values.
    """
    
    return re.sub('<(.*?)>', lambda m: replace.get(m.group(1), m.group(0)), value)
def add_version_field(data, replace):
    """
    Finds values within brackets <> in the data and adds a new field 'version' with value '0.1' to the replace dictionary.
    Parameters:
    data (str): The string to search for values within brackets.
    replace (dict): The dictionary to update with the new 'version' field.
    """
    found_values = [key for key in replace.keys() if re.search(f'<{key}>', str(data))]
    if found_values:
        data['version_number'] = replace[found_values[0]]
        return True
    else:
        return False

def version_check(version):
    """
    Checks if the version is preliminary or final. If version is <1 , then it is preliminary.
    If preliminary, updates the dataset with the preliminary template presets.
    """
    v_float = float(version)
    if v_float < 1:
        return 'preliminary'
    else:
        return 'final'
        
def add_path_fields(status,template, data):
    if 'ingest_location' in data and 'archive_location' in data:
        return
    if status == 'final':
        ingest_path = template['paths']['prod_ingest_base']
        archive_path =template['paths']['prod_archive_base']
    else:
        ingest_path = template['paths']['field_ingest_base']
        archive_path = template['paths']['field_archive_base']
    data['ingest_location'] = f'{ingest_path}/{data["dtype"]}'
    data['archive_location'] = f'{archive_path}/{data["dtype"]}'
        

def load_yaml_file(file_path):
    print(f'Loading {file_path}')
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def save_yaml_file(data, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file, width=1000)
        
def find_output_dir(output_base):
    """
    Finds the output directory where the files will be saved.
    """
    # Find all directories matching the pattern
    matching_dirs = glob.glob(output_base)

    # Check if any directories were found
    if matching_dirs and len(matching_dirs) > 1:
        print('Multiple matching directories found.')
        for i, dir in enumerate(matching_dirs):
            print(f'{i + 1}: {dir}')
        choice = int(input('Enter the number of the directory to use: ').strip())
        output_dir = matching_dirs[choice - 1]
        print(f'Selected configuration directory: {output_dir}')
        return output_dir
    elif matching_dirs:
        # Select the first match (or handle as needed)
        output_dir = matching_dirs[0]
        print(f'Found configuration directory: {output_dir}')
        return output_dir
    else:
        print('No matching directories found.')
        exit(1)

def process_yaml_file(yaml_path, replacements, aircraft_rep, template, versions,id_values, output_dir):
    data = load_yaml_file(yaml_path)
    for val in data:
        if 'cfg' in val: ##Skips the configuration section of the yaml file
            continue
        print(f'Processing {val}')
        valid_value_found = False
        for value in id_values.keys():
            if f'<{value}>' in str(data[val]) and id_values[value] is not None:
                valid_value_found = True
                continue
        if not valid_value_found:
            print(f'No archive id found for {val}')
            continue  # Exit the loop and continue with the next iteration of the outer loop
        stats = add_version_field(data[val], versions)
        if not stats:
            print(f'No version number found for {val}')
            break
        v_status = version_check(data[val]['version_number'])
        add_path_fields(v_status, template, data[val])
        replace_fields = global_fields + [v_status]
        for group in replace_fields:
            for field in template.get(group, []):
                if field == 'xlink_id':
                    ##For xlink ids, if the field already exists, append the new value to the existing value
                    try:
                        data[val][field] += f', {template[group][field]}'
                    except (KeyError, TypeError):
                        data[val][field] = template[group][field]
                    continue
                if field in data[val] and template[group][field] != data[val][field]:
                    response = input(f"The field '{field}' already exists. Do you wish to overwrite: {data[val][field]} \n with\n {template[group][field]}? \n(y to accept, anything else to reject): ").strip().lower()
                    if response != 'y':
                        print(f"Skipping {field}")
                        continue
                data[val][field] = template[group][field]
        
        
        for item in data[val]:
            if isinstance(data[val][item], str):
                if any(value in data[val][item] for value in replacements.keys()): 
                    data[val][item] = replace_variables(replacements, data[val][item])
                if any(value in data[val][item] for value in aircraft_rep.keys()):
                    data[val][item] = replace_variables(aircraft_rep, data[val][item])
        output_dir = find_output_dir(output_dir)
        output_path = os.path.join(output_dir, f'{val}.yml')
        result = [{k: v} for k, v in data[val].items()]
        save_yaml_file({'dataset': result}, output_path)

def replace_yaml_fields(input_file, main_dir, output_dir):
    template = load_yaml_file(input_file)
    replacements = template['variables']
    
    if 'archive_ids' in template:
        archive_ids = template.get('archive_ids', {})
        id_values = {key: value['id'] for key, value in archive_ids.items()}
        versions = {key: value['version_number'] for key, value in archive_ids.items()}
    replacements.update(id_values)
    aircraft_path = f"templates/{replacements['aircraft']}.yml"
    aircraft_rep = load_yaml_file(aircraft_path)

    for root, _, files in os.walk(main_dir):
        for file in files:
            if file.endswith('.yml'):
                yaml_path = os.path.join(root, file)
                process_yaml_file(yaml_path, replacements, aircraft_rep, template, versions,id_values, output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python replace_yaml.py <PROJECT_NAME>")
        sys.exit(1)
    project_name = sys.argv[1].upper()
    
    input_file = f'{project_folder}/project_template.yml'
    config_dir = f'{base}/base_config' #directory with yaml configuration files
    output_dir = f'/net/work/cfg-files/{project_name}*' #output directory to save files
    check = FieldsCheck() #Initialize the FieldsCheck class to check inputs against database values
    check_template(input_file,check.search_dict, check.tables)
    replace_yaml_fields(input_file, config_dir, output_dir)
    
    