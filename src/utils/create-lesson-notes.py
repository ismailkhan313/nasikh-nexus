#!/usr/bin/env python3
# flake8: noqa

import os
from config import OUTPUT_PATH_MARKDOWN, OUTPUT_PATH_TITLES_FILE

def get_lesson_titles(titles_filepath):
    """Reads lesson titles from the configured text file."""
    if not os.path.isfile(titles_filepath):
        print(f"❌ Error: The titles file was not found at: {titles_filepath}")
        return None
    try:
        with open(titles_filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ An error occurred while reading {titles_filepath}: {e}")
        return None

def create_markdown_files(output_directory, lesson_titles_list):
    """Creates markdown files with specified frontmatter in the output directory."""
    frontmatter = """---
created: 2025-06-11
tags:
  - literature-note/course/seekersguidance/kharida-albahiyya
  - islam/theology/ashari
---

"""
    if not os.path.isdir(output_directory):
        print(f"❌ Error: The output directory '{output_directory}' does not exist.")
        print("Please check the OUTPUT_PATH_MARKDOWN in your config.py file.")
        return

    print(f"This script will create {len(lesson_titles_list)} .md files in:")
    print(f"➡️ {output_directory}\n")

    for title in lesson_titles_list:
        filename = f"{title}.md"
        filepath = os.path.join(output_directory, filename)

        try:
            if os.path.exists(filepath):
                print(f"⚠️ Skipping '{filename}', file already exists.")
                continue
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
            print(f"✅ Created: {filename}")
        except IOError as e:
            print(f"❌ Error writing to file {filepath}: {e}")

if __name__ == "__main__":
    print("--- Starting Markdown File Creation ---")
    
    # Read from the titles file path
    lesson_titles = get_lesson_titles(OUTPUT_PATH_TITLES_FILE)

    if lesson_titles:
        # Write to the final markdown directory path
        create_markdown_files(OUTPUT_PATH_MARKDOWN, lesson_titles)
        print("\n--- Script finished. ---")
    else:
        print("\n--- Script aborted due to errors. ---")
