#!/usr/bin/env python
import os
import sys
import yaml
import glob
import argparse
from pathlib import Path

def find_yaml_file(output_dir, dataset_name):
    """Find the YAML file for the specified dataset in the output directory."""
    # Ensure the dataset name has .yml extension
    if not dataset_name.endswith('.yml'):
        dataset_name = f"{dataset_name.upper()}.yml"
    
    # Find all directories matching the pattern
    matching_dirs = glob.glob(output_dir)
    if not matching_dirs:
        print(f"No directories found matching pattern: {output_dir}")
        sys.exit(1)
    
    # If multiple matches, ask user to select one
    if len(matching_dirs) > 1:
        print('Multiple matching directories found:')
        for i, dir_path in enumerate(matching_dirs):
            print(f'{i + 1}: {dir_path}')
        choice = int(input('Enter the number of the directory to use: ').strip())
        selected_dir = matching_dirs[choice - 1]
    else:
        selected_dir = matching_dirs[0]
    
    # Look for the dataset file
    yaml_path = os.path.join(selected_dir, dataset_name)
    if not os.path.exists(yaml_path):
        print(f"Dataset file not found: {yaml_path}")
        sys.exit(1)
    
    return yaml_path

def update_yaml_file(yaml_path, version=None, ingest_location=None, filename_pattern=None):
    """Update specified fields in the YAML file."""
    try:
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        sys.exit(1)
    # Ensure the expected structure exists
    if 'dataset' not in data:
        print("Invalid YAML structure: 'dataset' key not found")
        sys.exit(1)
    # Track if we've made changes
    changes_made = False
    # Update version_number if provided
    if version:
        for item in data['dataset']:
            if 'version_number' in item:
                old_version = item['version_number']
                item['version_number'] = version
                print(f"Updated version_number: {old_version} -> {version}")
                changes_made = True
                break
        #check if version number is greater than 1.0
        if version and float(version) < 1.0:
            quality= 1 #set quality as preliminary
        else:
            quality = 2 #set quality as final
        for item in data['dataset']:
            if 'quality' in item:
                old_quality = item['quality']
                item['quality'] = quality
                print(f"Updated quality: {old_quality} -> {quality}")
                changes_made = True
                break
    # Update ingest_location if provided
    if ingest_location:
        for item in data['dataset']:
            if 'ingest_location' in item:
                old_location = item['ingest_location']
                item['ingest_location'] = ingest_location
                print(f"Updated ingest_location: {old_location} -> {ingest_location}")
                changes_made = True
                break

    # Update filename_pattern if provided
    if filename_pattern:
        for item in data['dataset']:
            if 'filename_pattern' in item:
                old_pattern = item['filename_pattern']
                item['filename_pattern'] = filename_pattern
                print(f"Updated filename_pattern: {old_pattern} -> {filename_pattern}")
                changes_made = True
                break
    
    if not changes_made:
        print("No changes were made to the file.")
        return
    
    # Save the updated YAML file
    try:
        with open(yaml_path, 'w') as file:
            yaml.dump(data, file, default_flow_style=False)
        print(f"Successfully updated {yaml_path}")
    except Exception as e:
        print(f"Error saving YAML file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Update fields in a dataset YAML file')
    parser.add_argument('project', help='Project name (e.g., CGWAVES)')
    parser.add_argument('dataset', help='Dataset name (e.g., ads, lrt, kml)')
    parser.add_argument('--version', '-v', help='New version number (e.g., 1.0)')
    parser.add_argument('--ingest', '-i', help='New ingest location')
    parser.add_argument('--pattern', '-p', help='New filename pattern')
    
    args = parser.parse_args()
    
    # Convert project name to uppercase
    project_name = args.project.upper()
    
    # Construct the output directory pattern
    output_dir = f'/net/work/cfg-files/{project_name}*'
    
    # Find the YAML file
    yaml_path = find_yaml_file(output_dir, args.dataset)
    
    # Update the YAML file
    update_yaml_file(
        yaml_path,
        version=args.version,
        ingest_location=args.ingest,
        filename_pattern=args.pattern
    )

if __name__ == "__main__":
    main()