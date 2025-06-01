#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
import time
from pathlib import Path # For easier path manipulation

# --- Configuration ---
# Name of the file containing your YouTube video URLs, one per line.
YOUTUBE_URLS_FILE = 'youtube_urls.txt'

# Base parent directory where batch-specific subfolders will be created.
BASE_OUTPUT_PARENT_DIR = Path('/Users/viz1er/Documents/audio-lectures')

# yt-dlp command arguments that remain static.
# The -o (output template) argument will be added dynamically.
YT_DLP_STATIC_ARGS = [
    'yt-dlp',
    '--downloader', 'aria2c',
    '--downloader-args', 'aria2c:-x16 -s16 -k1M',
    '-x', # Extract audio
    '--audio-format', 'mp3'
]

# --- Main Script Logic ---
def download_audio_from_urls(urls_file, base_output_parent_dir, static_yt_dlp_args):
    """
    Reads YouTube URLs from a file, prompts for a batch folder name,
    and downloads audio using yt-dlp into that batch-specific folder.

    Args:
        urls_file (str): Path to the file containing YouTube URLs.
        base_output_parent_dir (Path): The parent directory for batch folders.
        static_yt_dlp_args (list): List of static yt-dlp command arguments.
    """
    # Ensure the base parent directory exists
    try:
        base_output_parent_dir.mkdir(parents=True, exist_ok=True)
        print(f"Base directory for all audio batches: {base_output_parent_dir}")
    except OSError as e:
        print(f"Error: Could not create base output directory '{base_output_parent_dir}': {e}")
        return

    # Prompt for the name of the new subfolder for this batch
    batch_folder_name = input(f"Enter a name for the new folder to store this batch of audio (inside '{base_output_parent_dir}'): ").strip()

    if not batch_folder_name:
        print("Error: No batch folder name provided. Exiting.")
        return

    actual_output_dir = base_output_parent_dir / batch_folder_name
    try:
        actual_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Audio for this batch will be saved in: {actual_output_dir}")
    except OSError as e:
        print(f"Error: Could not create batch-specific output directory '{actual_output_dir}': {e}")
        return

    # Construct the output template for yt-dlp
    output_template = str(actual_output_dir / '%(title)s.%(ext)s')

    try:
        with open(urls_file, 'r') as f:
            youtube_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The URL file '{urls_file}' was not found.")
        print(f"Please make sure '{YOUTUBE_URLS_FILE}' exists in the same directory as the script or provide a full path.")
        return

    if not youtube_urls:
        print(f"No URLs found in '{urls_file}'. Please add YouTube video URLs to the file.")
        return

    print(f"\n--- Starting Audio Extraction from {len(youtube_urls)} URLs ---")
    print(f"Output MP3s will be saved to: {actual_output_dir}")

    for i, url in enumerate(youtube_urls):
        print(f"\nProcessing video {i+1}/{len(youtube_urls)}: {url}")
        
        # Construct the full command for the current URL, including the dynamic output path
        full_command = static_yt_dlp_args + ['-o', output_template, url]

        try:
            # Run the yt-dlp command
            process = subprocess.run(full_command, check=True, capture_output=False)
            print(f"Successfully extracted audio from: {url}")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio from {url}:")
            print(f"  Command: {' '.join(e.cmd)}")
            print(f"  Return Code: {e.returncode}")
            print("  Please check if yt-dlp and aria2c are installed and in your system's PATH.")
            print("  Also, verify the YouTube URL is valid and accessible.")
        except FileNotFoundError:
            print(f"Error: 'yt-dlp' or 'aria2c' command not found.")
            print("Please ensure yt-dlp and aria2c are installed and accessible in your system's PATH.")
            print("You might need to add their installation directory to your PATH environment variable.")
            break # If yt-dlp is not found, no point in continuing the loop
        except Exception as e:
            print(f"An unexpected error occurred while processing {url}: {e}")

        time.sleep(0.5) # Small delay

    print("\n--- All URLs Processed ---")
    print(f"Check the directory '{actual_output_dir}' for your extracted audio files.")

if __name__ == "__main__":
    download_audio_from_urls(YOUTUBE_URLS_FILE, BASE_OUTPUT_PARENT_DIR, YT_DLP_STATIC_ARGS)
