#!/usr/bin/env python3
# flake8: noqa

import os
import re # Still imported, though not strictly needed for the new filename logic

# Define the frontmatter content
frontmatter = """---
created: 2025-06-04
tags:
  - islam/fiqh/hanafi
  - literature-note/islamic-text/shurunbulali-nur-idah
  - literature-note/course/seekersguidance/rabbani-nur-idah-explained
---

"""

def get_lesson_titles(filename="lesson-titles.txt"):
    """
    Reads lesson titles from a specified text file.
    Each line in the file is expected to be a lesson title.
    """
    lesson_titles = []
    try:
        # Assume the script and the lesson-titles.txt file are in the same directory
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line: # Avoid adding empty lines
                    lesson_titles.append(stripped_line)
        if not lesson_titles:
            print(f"Warning: No lesson titles found in {filename}.")
        return lesson_titles
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found in the script's directory ({script_dir}).")
        print("Please create this file and add your lesson titles, one per line.")
        return None # Indicate failure
    except Exception as e:
        print(f"An error occurred while reading {filename}: {e}")
        return None # Indicate failure

def create_markdown_files(output_directory, lesson_titles_list):
    """
    Creates markdown files with specified frontmatter in the output directory.
    The output directory must already exist.
    Filenames will be exactly as in lesson_titles_list with .md appended.
    """
    # Check if the output directory exists and is a directory
    if not os.path.exists(output_directory):
        print(f"Error: The output directory '{output_directory}' does not exist.")
        print("Please create the directory or provide a valid existing path.")
        return # Exit if directory does not exist
    
    if not os.path.isdir(output_directory):
        print(f"Error: The path '{output_directory}' is not a directory.")
        print("Please provide a valid directory path.")
        return # Exit if path is not a directory

    # Process each lesson title
    for title in lesson_titles_list:
        # Use the title directly as the base for the filename
        filename_base = title
        
        # Ensure the filename_base is not empty
        if not filename_base:
            print(f"Skipping title due to empty filename: {title}")
            continue

        filename = f"{filename_base}.md"
        filepath = os.path.join(output_directory, filename)

        try:
            # Open the file in write mode
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
            print(f"Successfully created: {filepath}")
        except IOError as e:
            # This error can occur if, for example, there are permission issues
            # or the path becomes invalid for other reasons during the loop.
            print(f"Error writing to file {filepath}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred for title '{title}': {e}")

if __name__ == "__main__":
    # Get lesson titles from the file
    lesson_titles = get_lesson_titles()

    if lesson_titles is None: # Check if reading titles failed
        print("Exiting script due to issues reading lesson titles.")
    else:
        # Ask the user for the output directory
        while True:
            user_output_directory = input("Please enter the full path for the output directory: ").strip()
            if user_output_directory: # Check if the input is not empty
                # Further validation of the path format could be added here if desired,
                # but the create_markdown_files function now handles existence and type.
                break
            else:
                print("Output directory cannot be empty. Please enter a valid path.")
        
        print(f"\nThis script will attempt to create {len(lesson_titles)} .md files in the directory:")
        print(user_output_directory)
        print("The directory must already exist.")
        
        proceed = input("Do you want to proceed? (yes/no): ").strip().lower()
        if proceed == 'yes':
            create_markdown_files(user_output_directory, lesson_titles)
            print("\nScript finished.")
        else:
            print("Operation cancelled by the user.")

