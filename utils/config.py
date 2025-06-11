#!/usr/bin/env python3
# flake8: noqa

# --- Central Configuration for Your Workflow Scripts ---

import os

# --- Path 1: Output for Final Markdown Notes ---
OUTPUT_PATH_MARKDOWN = "/Users/viz1er/Codebase/obsidian-vault/02 - Literature Notes/Video Lectures/Minhaj al-Abideen Sulayman Van Ael"
# --- Path 2: Output for the Intermediate Titles File ---
OUTPUT_PATH_TITLES_FILE = "/Users/viz1er/Codebase/FlowScribe/utils/lesson-titles.txt"
# --- Path 3: Directory for .txt Files to be Renamed ---
PATH_FOR_RENAME = "/Users/viz1er/Codebase/obsidian-vault/02 - Literature Notes/Video Lectures/Minhaj al-Abideen Sulayman Van Ael/transcripts"


# --- DO NOT EDIT BELOW THIS LINE ---
# Helper function to ensure parent directory of a file exists.
def ensure_parent_dir_exists(filepath):
    """Checks if the directory for a given file path exists, and creates it if it doesn't."""
    parent_dir = os.path.dirname(filepath)
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir)
            print(f"✅ Created directory: {parent_dir}")
        except OSError as e:
            print(f"❌ Error creating directory {parent_dir}: {e}")
            raise
