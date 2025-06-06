#!/usr/bin/env python3
# flake8: noqa

import os

def list_files_to_txt(folder_path, output_file_path):
    """
    Lists all file names from a given folder and stores them in a .txt file.

    Args:
        folder_path (str): The path to the folder to scan.
        output_file_path (str): The full path to the output .txt file.
    """
    try:
        if not os.path.isdir(folder_path):
            print(f"Error: The folder '{folder_path}' was not found or is not a directory.")
            return

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        # Get file names from the given folder
        # os.listdir() gives all entries, os.path.isfile() filters for files
        all_entries = os.listdir(folder_path)
        file_names = [f for f in all_entries if os.path.isfile(os.path.join(folder_path, f))]

        # Write file names to the output text file
        with open(output_file_path, 'w') as f:
            for name in sorted(file_names): # Optional: sort the names
                f.write(name + '\n')
        
        print(f"Successfully saved {len(file_names)} file names to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ask for the folder path via a terminal prompt
    folder_path_input = input("Please enter the path to the folder whose file names you want to list: ")
    
    # Fixed output file path as per your request
    fixed_output_file = "/Users/viz1er/Codebase/FlowScribe/utils/lesson-titles.txt"
    
    if folder_path_input:
        list_files_to_txt(folder_path_input.strip(), fixed_output_file)
    else:
        print("No folder path was provided. Exiting.")