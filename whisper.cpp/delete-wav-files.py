#!/usr/bin/env python3
# flake8: noqa

import os
from pathlib import Path

def delete_wav_files(target_dir_str: str):
    """
    Deletes .wav files in the target directory (and subdirectories)
    after user confirmation.
    """
    target_dir = Path(target_dir_str).resolve() # Get absolute path

    if not target_dir.is_dir():
        print(f"Error: The path '{target_dir_str}' is not a valid directory or could not be resolved.")
        return

    print("\nWARNING: This script will search for and delete ALL .wav files")
    print(f"within the directory '{target_dir}' and all its subdirectories.")
    print("This action is IRREVERSIBLE.")
    print("")

    confirmation = input("Are you absolutely sure you want to proceed? (yes/no): ").strip().lower()

    if confirmation != "yes":
        print("Operation cancelled by the user.")
        return

    print(f"\nSearching for .wav files in '{target_dir}' to delete...")
    print("-----------------------------------------------------")

    deleted_count = 0
    found_files = 0
    deletion_errors = 0

    # Walk through the directory structure
    for root, dirs, files in os.walk(target_dir):
        current_path = Path(root)
        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(".wav"):
                found_files += 1
                wav_file_path = current_path / file
                print(f"Deleting: {wav_file_path}")
                try:
                    wav_file_path.unlink() # Deletes the file
                    deleted_count += 1
                except OSError as e:
                    deletion_errors += 1
                    print(f"Error deleting '{wav_file_path}': {e}")
                # No need for an explicit "-----------------------------------------------------"
                # after each file as the bash script didn't have it per file during deletion.

    print("-----------------------------------------------------")
    print("")

    if found_files == 0:
        print(f"No .wav files found to delete in '{target_dir}'.")
    else:
        print("Deletion process finished.")
        print(f"Found {found_files} .wav file(s).")
        print(f"Successfully deleted {deleted_count} .wav file(s).")
        if deletion_errors > 0:
            print(f"Encountered {deletion_errors} error(s) during deletion.")
        elif deleted_count < found_files: # Should not happen if no errors, but a safeguard
             print("Some files may not have been deleted due to unknown issues.")

if __name__ == "__main__":
    target_dir_input = input("Enter the path to the directory FROM WHICH you want to delete all .wav files: ")

    if not target_dir_input:
        print("Error: No directory path provided.")
        exit(1)

    delete_wav_files(target_dir_input)
