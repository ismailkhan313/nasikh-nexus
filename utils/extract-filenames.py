#!/usr/bin/env python3
# flake8: noqa

import os
import argparse
# --- MODIFIED: Import the source path from your config file ---
from config import OUTPUT_PATH_TITLES_FILE, PATH_FOR_RENAME, ensure_parent_dir_exists

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
        # Filter out subdirectories and hidden files like .DS_Store
        file_names = sorted([f for f in all_entries if os.path.isfile(os.path.join(source_directory, f)) and not f.startswith('.')])

        with open(output_file, 'w', encoding='utf-8') as f:
            for name in file_names:
                f.write(os.path.splitext(name)[0] + '\n')

        print(f"✅ Created: {os.path.basename(output_file)} with {len(file_names)} titles.")

    except Exception as e:
        print(f"❌ Error writing to file {output_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scan a source directory and save its filenames to the configured titles file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # --- MODIFIED: Changed from a required positional argument to an optional flag ---
    # It now has a '--' prefix, a default value from config.py, and help text.
    parser.add_argument(
        "-s", "--source",
        dest="source_directory",
        default=PATH_FOR_RENAME,
        help=(
            "The full path to the folder containing the source files.\n"
            f"(Defaults to the path in your config: {PATH_FOR_RENAME})"
        )
    )
    args = parser.parse_args()

    # The rest of your script now works perfectly with either the default or a custom path.
    print(f"➡️ Reading from: {args.source_directory}")
    print(f"➡️ Writing titles to:   {OUTPUT_PATH_TITLES_FILE}\n")

    list_files_to_txt(args.source_directory, OUTPUT_PATH_TITLES_FILE)