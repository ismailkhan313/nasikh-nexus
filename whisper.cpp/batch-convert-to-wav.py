#!/usr/bin/env python3
# flake8: noqa

import os
import subprocess
import shutil # To check for ffmpeg executable
from pathlib import Path

def check_ffmpeg():
    """Checks if ffmpeg is installed and accessible."""
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed or not found in your PATH.")
        print("Please install ffmpeg to use this script.")
        print("On macOS, you can install it using Homebrew: brew install ffmpeg")
        print("On Debian/Ubuntu, you can install it using: sudo apt update && sudo apt install ffmpeg")
        return False
    return True

def convert_audio_files(target_dir_str: str):
    """
    Converts .mp3 and .m4a files in the target directory (and subdirectories)
    to .wav format (16kHz, mono).
    """
    target_dir = Path(target_dir_str).resolve() # Get absolute path

    if not target_dir.is_dir():
        print(f"Error: The path '{target_dir_str}' is not a valid directory or could not be resolved.")
        return

    output_wav_subdir_name = "converted_to_wav"
    output_wav_dir = target_dir / output_wav_subdir_name

    try:
        output_wav_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create output directory '{output_wav_dir}': {e}")
        return

    print(f"\nTarget audio directory: '{target_dir}'")
    print("Searching for .mp3 and .m4a files...")
    print(f"(Excluding the output subdirectory '{output_wav_subdir_name}').")
    print(f"Converted .wav files will be saved in '{output_wav_dir}'.")
    print("-----------------------------------------------------")

    processed_count = 0
    conversion_errors = 0

    # Walk through the directory structure
    for root, dirs, files in os.walk(target_dir):
        current_path = Path(root)

        # Skip the output directory itself to avoid processing already converted files
        if output_wav_dir.resolve() in current_path.parents or current_path == output_wav_dir.resolve():
            # To prevent descending into the output directory, we can modify 'dirs' in-place
            if output_wav_subdir_name in dirs:
                dirs.remove(output_wav_subdir_name)
            continue

        for file in files:
            file_lower = file.lower()
            if file_lower.endswith(".mp3") or file_lower.endswith(".m4a"):
                processed_count += 1
                audio_file_path = current_path / file

                print(f"Processing audio file ({processed_count}): {audio_file_path}")

                base_name = Path(file).stem # Gets filename without extension
                output_wav_name = f"{base_name}.wav"
                output_wav_path = output_wav_dir / output_wav_name

                print(f"Converting '{file}' to '{output_wav_name}'...")

                # Construct the ffmpeg command
                # -i: input file
                # -ar 16000: audio sample rate 16kHz
                # -ac 1: audio channels 1 (mono)
                # -c:a pcm_s16le: audio codec PCM signed 16-bit little-endian
                # -loglevel error: only show errors
                # -y: overwrite output file without asking
                cmd = [
                    "ffmpeg",
                    "-i", str(audio_file_path),
                    "-ar", "16000",
                    "-ac", "1",
                    "-c:a", "pcm_s16le",
                    str(output_wav_path),
                    "-loglevel", "error",
                    "-y"
                ]

                try:
                    # For debugging, print the command:
                    # print(f"Executing: {' '.join(cmd)}")
                    process = subprocess.run(cmd, check=True, capture_output=True, text=True)
                    print(f"Successfully converted to: {output_wav_path}")
                except subprocess.CalledProcessError as e:
                    conversion_errors += 1
                    print(f"Error converting '{file}'.")
                    print(f"Command failed: {' '.join(e.cmd)}")
                    if e.stdout:
                        print(f"FFmpeg stdout:\n{e.stdout}")
                    if e.stderr:
                        print(f"FFmpeg stderr:\n{e.stderr}")
                except FileNotFoundError: # Should be caught by check_ffmpeg, but good practice
                    print("Error: ffmpeg command not found. Make sure it's installed and in PATH.")
                    return # Critical error, stop processing
                print("-----------------------------------------------------")

    print("\nBatch conversion finished.")
    if processed_count == 0:
        print(f"No .mp3 or .m4a files found to convert in '{target_dir}' (excluding the '{output_wav_subdir_name}' subdirectory).")
    else:
        print(f"Processed {processed_count} file(s).")
        if conversion_errors > 0:
            print(f"Encountered {conversion_errors} error(s) during conversion.")
    print(f"All successfully converted .wav files are located in: {output_wav_dir}")


if __name__ == "__main__":
    if not check_ffmpeg():
        exit(1)

    target_dir_input = input("Enter the path to the directory containing your audio files: ")

    if not target_dir_input:
        print("Error: No directory path provided.")
        exit(1)

    convert_audio_files(target_dir_input)
