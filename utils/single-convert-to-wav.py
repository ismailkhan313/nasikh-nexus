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

def convert_audio_file(input_file_path_str: str):
    """
    Converts a single .mp3 or .m4a file to .wav format (16kHz, mono).
    The output .wav file is saved in the same directory as the input file.
    """
    input_file_path = Path(input_file_path_str).resolve() # Get absolute path

    if not input_file_path.is_file():
        print(f"Error: The path '{input_file_path_str}' is not a valid file or could not be resolved.")
        return

    file_lower = input_file_path.name.lower()
    if not (file_lower.endswith(".mp3") or file_lower.endswith(".m4a")):
        print(f"Error: Input file '{input_file_path.name}' must be an .mp3 or .m4a file.")
        print("Supported formats are .mp3 and .m4a.")
        return

    output_dir = input_file_path.parent
    base_name = input_file_path.stem # Gets filename without extension
    output_wav_name = f"{base_name}.wav"
    output_wav_path = output_dir / output_wav_name

    print(f"\nInput audio file: '{input_file_path}'")
    print(f"Output .wav file will be saved as: '{output_wav_path}'")
    print("-----------------------------------------------------")

    print(f"Converting '{input_file_path.name}' to '{output_wav_name}'...")

    # Construct the ffmpeg command
    # -i: input file
    # -ar 16000: audio sample rate 16kHz
    # -ac 1: audio channels 1 (mono)
    # -c:a pcm_s16le: audio codec PCM signed 16-bit little-endian
    # -loglevel error: only show errors
    # -y: overwrite output file without asking
    cmd = [
        "ffmpeg",
        "-i", str(input_file_path),
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        str(output_wav_path),
        "-loglevel", "error",
        "-y"
    ]

    conversion_error_occurred = False
    try:
        # For debugging, print the command:
        # print(f"Executing: {' '.join(cmd)}")
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully converted to: {output_wav_path}")
    except subprocess.CalledProcessError as e:
        conversion_error_occurred = True
        print(f"Error converting '{input_file_path.name}'.")
        print(f"Command failed: {' '.join(e.cmd)}")
        if e.stdout:
            print(f"FFmpeg stdout:\n{e.stdout}")
        if e.stderr:
            print(f"FFmpeg stderr:\n{e.stderr}")
    except FileNotFoundError: # Should be caught by check_ffmpeg, but good practice
        conversion_error_occurred = True
        print("Error: ffmpeg command not found. Make sure it's installed and in PATH.")
        return # Critical error, stop processing
    print("-----------------------------------------------------")

    print("\nConversion finished.")
    if conversion_error_occurred:
        print(f"An error occurred during the conversion of '{input_file_path.name}'.")
    else:
        print(f"File '{input_file_path.name}' was successfully converted.")
        print(f"Output saved to: {output_wav_path}")


if __name__ == "__main__":
    if not check_ffmpeg():
        exit(1)

    target_file_input = input("Enter the path to your audio file (.mp3 or .m4a): ")

    if not target_file_input:
        print("Error: No file path provided.")
        exit(1)

    convert_audio_file(target_file_input)