#!/usr/bin/env python3
# flake8: noqa

import os
import argparse
from config import OUTPUT_PATH_TITLES_FILE, ensure_parent_dir_exists

def list_files_to_txt(source_directory, output_file):
    """
    Scans a source directory, extracts the base filenames (without extension),
    and saves them to a specified output text file.
    """
    if not os.path.isdir(source_directory):
        print(f"❌ Error: The source directory '{source_directory}' does not exist.")
        return

    try:
        ensure_parent_dir_exists(output_file)
        all_entries = os.listdir(source_directory)
        file_names = sorted([f for f in all_entries if os.path.isfile(os.path.join(source_directory, f))])

        with open(output_file, 'w', encoding='utf-8') as f:
            for name in file_names:
                f.write(os.path.splitext(name)[0] + '\n')

        # Use the consistent success message format
        print(f"✅ Created: {os.path.basename(output_file)} with {len(file_names)} titles.")

    except Exception as e:
        # Use the consistent error message format
        print(f"❌ Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan a source directory and save its filenames to the configured titles file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "source_directory",
        help="The full path to the folder containing the source files."
    )
    args = parser.parse_args()

    print(f"➡️ Reading from: {args.source_directory}")
    print(f"➡️ Writing titles to:   {OUTPUT_PATH_TITLES_FILE}\n")
    
    list_files_to_txt(args.source_directory, OUTPUT_PATH_TITLES_FILE)
