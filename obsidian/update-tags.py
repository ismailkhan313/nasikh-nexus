#!/usr/bin/env python3
# flake8: noqa

import os
import yaml

def update_obsidian_tag(folder_path, files_to_update, old_tag_part, new_tag):
    """
    Updates a specific tag in the frontmatter of selected Obsidian markdown files.

    Args:
        folder_path (str): The path to the folder containing the markdown files.
        files_to_update (list): A list of markdown filenames (e.g., ['file1.md', 'file2.md']).
        old_tag_part (str): A unique part of the tag you want to replace (e.g., 'islam/quranic-sciences/tafsir').
        new_tag (str): The complete new tag to replace the old one with.
    """
    print(f"Starting tag update process in: {folder_path}")
    print(f"Files to be updated: {', '.join(files_to_update)}")

    for filename in files_to_update:
        filepath = os.path.join(folder_path, filename)

        if not os.path.exists(filepath):
            print(f"Warning: File not found - {filepath}. Skipping.")
            continue
        if not filename.endswith(".md"):
            print(f"Warning: File is not a markdown file - {filepath}. Skipping.")
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content into frontmatter and body
            parts = content.split('---', 2)
            if len(parts) < 3:
                print(f"Warning: No valid frontmatter found in {filename}. Skipping.")
                continue

            frontmatter_str = parts[1].strip()
            body = parts[2].strip()

            # Parse frontmatter
            frontmatter = yaml.safe_load(frontmatter_str)

            if 'tags' in frontmatter and isinstance(frontmatter['tags'], list):
                updated_tags = []
                tag_found_and_updated = False
                for tag in frontmatter['tags']:
                    if isinstance(tag, str) and old_tag_part in tag:
                        if not tag_found_and_updated: # Only replace the first occurrence if multiple similar tags exist
                            updated_tags.append(new_tag)
                            tag_found_and_updated = True
                        else:
                            updated_tags.append(tag) # Keep other tags
                    else:
                        updated_tags.append(tag)
                
                if tag_found_and_updated:
                    frontmatter['tags'] = updated_tags
                    
                    # Reconstruct the file content
                    updated_frontmatter_str = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False, allow_unicode=True)
                    new_content = f"---\n{updated_frontmatter_str}---\n{body}"

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Successfully updated tag in: {filename}")
                else:
                    print(f"No matching tag ('{old_tag_part}') found in {filename}. Skipping.")
            else:
                print(f"No 'tags' list found in frontmatter of {filename}. Skipping.")

        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {filename}: {e}. Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred with {filename}: {e}. Skipping.")

def read_filenames_from_file(filepath):
    """
    Reads filenames from a specified text file, one filename per line.

    Args:
        filepath (str): The path to the text file containing filenames.

    Returns:
        list: A list of filenames, stripped of whitespace.
    """
    filenames = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                filename = line.strip()
                if filename and not filename.startswith('#'): # Ignore empty lines and lines starting with # (for comments)
                    filenames.append(filename)
    except FileNotFoundError:
        print(f"Error: Filenames file not found at {filepath}.")
        return None
    except Exception as e:
        print(f"Error reading filenames file: {e}")
        return None
    return filenames

if __name__ == "__main__":
    # --- Configuration ---
    # The part of the tag to identify for replacement. Make it specific enough!
    OLD_TAG_PART_TO_IDENTIFY = 'islam/quranic-sciences/tafsir' 
    # The complete new tag you want to set
    NEW_TAG = 'islam/quranic-sciences/tafsir/67-mulk'
    # The name of the file containing the list of markdown filenames
    FILENAMES_FILE = 'filenames.txt'
    # -------------------

    # Get folder path from user
    folder = input("Enter the full path to the Obsidian folder: ").strip()
    if not os.path.isdir(folder):
        print("Error: The provided path is not a valid directory. Exiting.")
        exit()

    # Read filenames from the specified file
    files_to_process = read_filenames_from_file(FILENAMES_FILE)
    
    if files_to_process is None: # An error occurred while reading the file
        print("Could not read filenames from the specified file. Exiting.")
        exit()
    elif not files_to_process:
        print(f"No filenames found in {FILENAMES_FILE}. Please ensure it's not empty or only contains comments. Exiting.")
        exit()
    else:
        print(f"\nRead {len(files_to_process)} filenames from {FILENAMES_FILE}.")

    update_obsidian_tag(folder, files_to_process, OLD_TAG_PART_TO_IDENTIFY, NEW_TAG)
    print("\nProcess complete.")