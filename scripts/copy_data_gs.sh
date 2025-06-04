#!/bin/bash
# Default destination directory
DEST_DIR="/var/r1/$PROJECT"
echo "Files will be copied to: $DEST_DIR"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Function to process files from selected source directory
process_files() {
    local source_dir=$1/$PROJECT
    local copy_dir=$2

    # Confirm copy
    read -p "Copy files from $source_dir to $copy_dir? (y/n): " confirm
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        mkdir -p "$copy_dir"

        # Process files one by one
        echo -e "\nProcessing files from $source_dir:"
        read -p "Input flight designation or return to step through all files: " flight
        while IFS= read -r file; do
            # Match flight number entered; if entered "", then match everything
            if echo "$file" | grep -iq "$flight"; then # Check if file name contains flight (case-insensitive)
                if [[ -f "$source_dir/$file" ]]; then # File exists
                    size=$(du -h "$source_dir/$file" | cut -f1)
                    echo "File: $file ($size)"
                    # Corrected read command:
                    read -p "Copy this file? (y/n): " copy_file < /dev/tty
                    if [[ "$copy_file" == "y" || "$copy_file" == "Y" ]]; then
                        echo "Copying: $file"
                        cp -v "$source_dir/$file" "$copy_dir/"
                        echo "Copied successfully."
                    else
                        echo "Skipping file."
                    fi
                fi
            fi
        done < <(ls -1 "$source_dir") # Input redirection for the while loop
        return 0
    else
        echo "Copy cancelled."
        return 1
    fi
}

# Function to select a drive from a list
select_drive() {
    local drive_list=("$@")
    local selected_index=0
    
    # Show detected drives
    echo "Available drives:"
    for i in "${!drive_list[@]}"; do
        echo "[$((i+1))] ${drive_list[$i]}"
    done

    # Select drive
    if [[ ${#drive_list[@]} -gt 1 ]]; then
        read -p "Select drive number to copy from: " selected_num
        selected_index=$((selected_num-1))
    fi
    
    if [[ $selected_index -ge 0 && $selected_index -lt ${#drive_list[@]} ]]; then
        echo "${drive_list[$selected_index]}"
	source_dir=${drive_list[$selected_index]}
        return 0
    else
        echo "Invalid selection."
        return 1
    fi
}

# Get list of mounted drives in /run/media/ads (change if different mounting location)
get_drives() {
    local drives=()
    
    # Check if the base directory exists
    if [[ ! -d "/run/media/ads" ]]; then
        echo "Directory /run/media/ads does not exist" >&2
        return
    fi
    
    # List all subdirectories directly under /run/media/ads
    for drive in /run/media/ads/*; do
        if [[ -d "$drive" ]]; then
            drives+=("$drive")
        fi
    done
    
    echo "${drives[@]}"
}


# Main script
drives=($(get_drives))

if [[ ${#drives[@]} -gt 0 ]]; then
    echo -e "\nFound connected drives:"
    for i in "${!drives[@]}"; do
        echo "[$((i+1))] ${drives[$i]}"
    done
    read -p "Use an already connected drive? (y/n): " use_existing
    if [[ "$use_existing" == "y" || "$use_existing" == "Y" ]]; then
        select_drive "${drives[@]}"
        echo $source_dir
       	if [[ -n "$source_dir" ]]; then
            process_files "$source_dir" "$DEST_DIR"
            echo "Script completed. Press Enter to exit."
            read dummy_var
	    exit $?
        fi
    fi
fi

echo "Monitoring for new drives. Connect your drive now..."
echo "Press Ctrl+C to exit"

# Get initial list of mounted drives
initial_drives=$(lsblk -o NAME,MOUNTPOINT | grep -v "^NAME" | grep -v "^$" | grep -v " $" | grep -v "\[SWAP\]" | grep -v " /$")

while true; do
    # Get current list of drives
    current_drives=$(lsblk -o NAME,MOUNTPOINT | grep -v "^NAME" | grep -v "^$" | grep -v " $" | grep -v "\[SWAP\]" | grep -v " /$")
    
    # Check for new drives
    if [[ "$current_drives" != "$initial_drives" ]]; then
        echo -e "\nNew drive detected!"
        
        # Find new drive mountpoints
        new_drive_list=()
        while IFS= read -r line; do
            if ! echo "$initial_drives" | grep -q "$line"; then
                mount_point=$(echo "$line" | awk '{print $2}')
                if [[ -n "$mount_point" ]]; then
                    new_drive_list+=("$mount_point")
                fi
            fi
        done <<< "$current_drives"
        
        source_dir=$(select_drive "${new_drive_list[@]}")
        if [[ -n "$source_dir" ]]; then
       	    if process_files "$source_dir" "$DEST_DIR"; then
                echo "Script completed. Press Enter to exit."
		read dummy_var
		exit 0
            fi
        fi
        
        # Update initial drives list
        initial_drives="$current_drives"
    fi
    
    sleep 2
done
