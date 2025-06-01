#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
import time

# --- Configuration ---
# Name of the file containing your YouTube video URLs, one per line.
YOUTUBE_URLS_FILE = 'youtube_urls.txt'

# Directory where the extracted MP3s will be saved.
# If it doesn't exist, the script will create it.
OUTPUT_DIRECTORY = 'extracted_audio_lectures'

# yt-dlp command arguments.
# This uses your preferred downloader and audio extraction settings.
# The URL will be appended by the script for each video.
YT_DLP_BASE_COMMAND = [
    'yt-dlp',
    '--downloader', 'aria2c',
    '--downloader-args', 'aria2c:-x16 -s16 -k1M',
    '-x',  # Extract audio
    '--audio-format', 'mp3',
    '-o', os.path.join(OUTPUT_DIRECTORY, '%(title)s.%(ext)s') # Output template: saves to OUTPUT_DIRECTORY with title as filename
]

# --- Main Script Logic ---
def download_audio_from_urls(urls_file, output_dir, base_command):
    """
    Reads YouTube URLs from a file and downloads audio using yt-dlp.

    Args:
        urls_file (str): Path to the file containing YouTube URLs.
        output_dir (str): Directory to save the extracted audio files.
        base_command (list): List of base yt-dlp command arguments.
    """
    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)

    try:
        with open(urls_file, 'r') as f:
            youtube_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The URL file '{urls_file}' was not found.")
        print("Please make sure 'youtube_urls.txt' exists in the same directory as the script.")
        return

    if not youtube_urls:
        print(f"No URLs found in '{urls_file}'. Please add YouTube video URLs to the file.")
        return

    print(f"--- Starting Audio Extraction from {len(youtube_urls)} URLs ---")
    print(f"Output MP3s will be saved to: {os.path.abspath(output_dir)}")

    for i, url in enumerate(youtube_urls):
        print(f"\nProcessing video {i+1}/{len(youtube_urls)}: {url}")
        
        # Construct the full command for the current URL
        full_command = base_command + [url]

        try:
            # Run the yt-dlp command
            # `capture_output=False` allows yt-dlp's progress to be printed directly to your terminal
            process = subprocess.run(full_command, check=True, capture_output=False)
            print(f"Successfully extracted audio from: {url}")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio from {url}:")
            print(f"  Command: {' '.join(e.cmd)}")
            print(f"  Return Code: {e.returncode}")
            # If capture_output was True, you'd print e.stdout and e.stderr here
            # print(f"  Stdout: {e.stdout.decode()}")
            # print(f"  Stderr: {e.stderr.decode()}")
            print("  Please check if yt-dlp and aria2c are installed and in your system's PATH.")
            print("  Also, verify the YouTube URL is valid and accessible.")
        except FileNotFoundError:
            print(f"Error: 'yt-dlp' or 'aria2c' command not found.")
            print("Please ensure yt-dlp and aria2c are installed and accessible in your system's PATH.")
            print("You might need to add their installation directory to your PATH environment variable.")
        except Exception as e:
            print(f"An unexpected error occurred while processing {url}: {e}")

        time.sleep(0.5) # Small delay to be polite and avoid overwhelming resources

    print("\n--- All URLs Processed ---")
    print("Check the output directory for your extracted audio files.")

if __name__ == "__main__":
    download_audio_from_urls(YOUTUBE_URLS_FILE, OUTPUT_DIRECTORY, YT_DLP_BASE_COMMAND)