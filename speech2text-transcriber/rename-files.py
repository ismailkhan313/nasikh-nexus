#!/usr/bin/env python3
# flake8: noqa

import os
import re
import argparse
from collections import defaultdict

def parse_filename(filename):
    """
    Parses a filename to extract episode number, suffix, and the title part.
    Returns a dictionary with 'num', 'suffix', 'title_part', 'is_intro'.
    'num' will be an int. 'suffix' will be a letter or empty string (or specific intro key).
    'title_part' is the part of the filename to keep after the new number.
    'is_intro' is a boolean.
    """
    base, ext = os.path.splitext(filename)

    # Pattern 1: Numbered episode (e.g., "... - 06 - Title", "... - 06 b - Title")
    # This regex looks for " - number [optional_letter_suffix] - The Rest of The Title"
    # The (.+) captures "The Rest of The Title"
    numbered_match = re.search(r" - (\d+)\s*([a-zA-Z])?\s*-\s*(.+)", base)
    if numbered_match:
        num_str, suffix_char, title_content = numbered_match.groups()
        return {
            "num": int(num_str),
            "suffix": suffix_char.lower() if suffix_char else "",
            "title_part": title_content.strip() + ext,
            "is_intro": False,
        }

    # Pattern 2: Introduction episode (e.g., "... - Introduction - Title", "... - Introduction (Part Two) - Title")
    # This regex looks for " - Introduction..." and captures everything from "Introduction" onwards as the title part.
    intro_match = re.search(r" - (Introduction.*?)$", base)
    if intro_match:
        title_content = intro_match.group(1).strip()
        
        # Determine a sortable suffix for introduction parts
        suffix_for_intro = "" # Default for plain "Introduction"
        if "(Part Two)" in title_content or "(Part 2)" in title_content.replace("Two","2"):
            suffix_for_intro = "part2"
        elif "(Part One)" in title_content or "(Part 1)" in title_content.replace("One","1"):
            suffix_for_intro = "part1"
        # Add more specific intro suffixes if needed, ensuring alphabetical sort order

        return {
            "num": 0,  # Assign 0 for intros for sorting purposes
            "suffix": suffix_for_intro,
            "title_part": title_content + ext,
            "is_intro": True,
        }
    
    # Fallback: if a file starts directly with a number like "01 - Title.m4a"
    # This wasn't explicitly in the examples but could be a common case.
    direct_numbered_match = re.match(r"^(\d+)\s*([a-zA-Z])?\s*-\s*(.+)", base)
    if direct_numbered_match:
        num_str, suffix_char, title_content = direct_numbered_match.groups()
        return {
            "num": int(num_str),
            "suffix": suffix_char.lower() if suffix_char else "",
            "title_part": title_content.strip() + ext,
            "is_intro": False,
        }

    return None # Unable to parse

def process_directory(directory_path, dry_run=True):
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found: {directory_path}")
        return

    print(f"Processing directory: {directory_path}")
    if dry_run:
        print("--- DRY RUN MODE --- (No files will be changed)")

    # Consider only .m4a files, can be changed if needed
    filenames = [f for f in os.listdir(directory_path) 
                 if os.path.isfile(os.path.join(directory_path, f)) and f.lower().endswith('.m4a')]

    parsed_files_info = []
    for fname in filenames:
        info = parse_filename(fname)
        if info:
            parsed_files_info.append({
                "original_name": fname,
                **info  # num, suffix, title_part, is_intro
            })
        else:
            print(f"Warning: Could not parse filename: {fname}. Skipping.")

    # Sort files:
    # Primary key: 'num' (Introduction files with num=0 will come first)
    # Secondary key: 'suffix' (e.g., '' < 'a' < 'b'; for intros: '' < 'part1' < 'part2')
    def sort_key(file_info):
        return (file_info["num"], file_info["suffix"])

    parsed_files_info.sort(key=sort_key)

    # Group files by their main number to handle sub-numbering (e.g., 06 -> 06-1, 06-2)
    grouped_by_main_num = defaultdict(list)
    for pf_info in parsed_files_info:
        grouped_by_main_num[pf_info["num"]].append(pf_info)

    renaming_plan = []
    
    # Iterate through sorted unique main numbers to maintain overall order
    sorted_main_numbers = sorted(grouped_by_main_num.keys())

    for main_num in sorted_main_numbers:
        files_in_group = grouped_by_main_num[main_num]
        # files_in_group should already be sorted by suffix due to the initial sort
        # and how they were added to the list in defaultdict.
        # To be absolutely sure, you could re-sort here by suffix if complex suffixes arise:
        # files_in_group.sort(key=lambda x: x["suffix"])

        base_num_str = f"{main_num:02d}" # Format as 00, 01, 06, etc.

        if len(files_in_group) > 1: # Multiple parts for this number, requires sub-indexing
            for i, file_info in enumerate(files_in_group):
                sub_index = i + 1
                new_num_part = f"{base_num_str}-{sub_index}"
                new_name = f"{new_num_part} - {file_info['title_part']}"
                renaming_plan.append((file_info["original_name"], new_name))
        else: # Single file for this main_num
            file_info = files_in_group[0]
            # For single files, use the base number directly (e.g., "07 - Title")
            new_name = f"{base_num_str} - {file_info['title_part']}"
            renaming_plan.append((file_info["original_name"], new_name))

    # Execute or print renaming plan
    if not renaming_plan:
        print("No files found or parsed for renaming.")
        return

    print("\nRenaming Plan:")
    for old_name, new_name in renaming_plan:
        old_path = os.path.join(directory_path, old_name)
        new_path = os.path.join(directory_path, new_name)

        if old_name == new_name:
            print(f"Identical: '{old_name}' (No change needed)")
            continue
        
        action_prefix = "Would rename" if dry_run else "Renaming"
        print(f"{action_prefix}: '{old_name}'\n          TO: '{new_name}'")

        if not dry_run:
            try:
                if os.path.exists(new_path):
                    print(f"  Error: Target file '{new_name}' already exists. Skipping rename of '{old_name}'.")
                else:
                    os.rename(old_path, new_path)
                    print(f"  Successfully renamed.")
            except OSError as e:
                print(f"  Error renaming '{old_name}' to '{new_name}': {e}")
        elif os.path.exists(new_path) and old_name != new_name : # Check for potential overwrite in dry run
            print(f"  Warning (dry-run): Target file '{new_name}' would be overwritten if it's different from the source.")


    if dry_run:
        print("\n--- DRY RUN COMPLETE ---")
        print("No files were actually changed. Run without --dry-run to apply changes.")
    else:
        print("\n--- RENAMING COMPLETE ---")

def main():
    parser = argparse.ArgumentParser(
        description="Rename audio files (.m4a) to a sequential numbered format. "\
                    "Example: 'Lecture - 01 - Topic A.m4a' -> '01 - Topic A.m4a', "\
                    "'Lecture - 06 - Part1.m4a' & 'Lecture - 06 b - Part2.m4a' -> '06-1 - Part1.m4a' & '06-2 - Part2.m4a'."
    )
    parser.add_argument("path", help="Path to the directory containing the .m4a files.")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be renamed without actually performing any renaming operations."
    )
    args = parser.parse_args()

    process_directory(args.path, args.dry_run)

if __name__ == "__main__":
    main()