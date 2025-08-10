#!/usr/bin/env python3
# flake8: noqa

import os
import argparse
from config import OUTPUT_PATH_TITLES_FILE, PATH_FOR_RENAME

def batch_rename_files(target_directory, dry_run=False):
    """
    Batch renames .txt files in a directory based on a list of titles
    from the centrally configured titles file.
    """
    if not os.path.isdir(target_directory):
        print(f"❌ Error: The target directory does not exist: {target_directory}")
        return

    if not os.path.isfile(OUTPUT_PATH_TITLES_FILE):
        print(f"❌ Error: The titles file does not exist at: {OUTPUT_PATH_TITLES_FILE}")
        return

    print(f"Scanning directory: {os.path.abspath(target_directory)}")
    print(f"Reading titles from: {OUTPUT_PATH_TITLES_FILE}\n")

    try:
        with open(OUTPUT_PATH_TITLES_FILE, 'r', encoding='utf-8') as f:
            new_titles = [line.strip() for line in f if line.strip()]
        if not new_titles:
            print("⚠️ Warning: No valid titles found in the titles file.")
            return
    except Exception as e:
        print(f"❌ Error reading titles file: {e}")
        return

    try:
        txt_files = sorted([f for f in os.listdir(target_directory) if f.lower().endswith('.txt')])
    except Exception as e:
        print(f"❌ Error accessing files in the directory: {e}")
        return

    if not txt_files:
        print("ℹ️ No .txt files found to rename in the directory.")
        return

    print(f"Found {len(txt_files)} .txt files and {len(new_titles)} new titles.")
    if len(txt_files) != len(new_titles):
        print("\n⚠️ WARNING: File count and title count do not match. Renaming will be partial.\n")

    rename_count = min(len(txt_files), len(new_titles))
    print("--- Starting Rename Process ---")
    if dry_run:
        print("DRY RUN MODE: No files will be renamed.\n")

    renamed_files_count = 0
    for i in range(rename_count):
        old_filename = txt_files[i]
        new_basename = new_titles[i]
        new_filename = f"{new_basename}.txt"

        old_filepath = os.path.join(target_directory, old_filename)
        new_filepath = os.path.join(target_directory, new_filename)

        if dry_run:
            print(f"DRY RUN: '{old_filename}' -> '{new_filename}'")
        else:
            try:
                os.rename(old_filepath, new_filepath)
                print(f"✅ Renamed: '{new_filename}'")
                renamed_files_count += 1
            except FileExistsError:
                print(f"⚠️ Skipping '{new_filename}', file already exists.")
            except Exception as e:
                print(f"❌ Error renaming {old_filename}: {e}")

    print("\n--- Process Complete ---")
    if not dry_run:
        print(f"Successfully renamed {renamed_files_count} out of {rename_count} targeted files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch rename .txt files in the configured directory using the central titles file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate renames without changing any filenames."
    )
    args = parser.parse_args()

    print(f"➡️ Using target directory from config: {PATH_FOR_RENAME}")
    
    batch_rename_files(PATH_FOR_RENAME, args.dry_run)
