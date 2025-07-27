#!/usr/bin/env python3
# flake8: noqa

import os
import subprocess
import shutil
import argparse
from pathlib import Path

def check_ffmpeg():
    """Checks if ffmpeg is installed and accessible in the system's PATH."""
    if shutil.which("ffmpeg") is None:
        print("❌ Error: ffmpeg is not installed or not found in your PATH.")
        print("Please install ffmpeg to use this script.")
        print("On macOS (via Homebrew): brew install ffmpeg")
        print("On Debian/Ubuntu: sudo apt update && sudo apt install ffmpeg")
        return False
    return True

def run_ffmpeg_conversion(input_path: Path, output_path: Path) -> bool:
    """
    Runs the ffmpeg command to convert a single audio file.

    Args:
        input_path: The Path object for the source audio file.
        output_path: The Path object for the destination .wav file.

    Returns:
        True if conversion was successful, False otherwise.
    """
    print(f"Converting '{input_path.name}'...")
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-ar", "16000",       # Audio sample rate: 16kHz
        "-ac", "1",           # Audio channels: 1 (mono)
        "-c:a", "pcm_s16le",  # Codec: PCM signed 16-bit little-endian
        str(output_path),
        "-loglevel", "error", # Only show errors
        "-y"                  # Overwrite output file without asking
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Created: {output_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error converting {input_path.name}:")
        print(f"   FFmpeg stderr: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print("❌ Error: ffmpeg command not found during conversion.")
        return False

def convert_single_file(file_path: Path):
    """
    Handles the conversion of a single audio file.
    The output .wav is saved in the same directory.
    """
    if not (file_path.name.lower().endswith(".mp3") or file_path.name.lower().endswith(".m4a")):
        print(f"❌ Error: Input file '{file_path.name}' is not a supported type (.mp3, .m4a).")
        return

    output_wav_path = file_path.with_suffix('.wav')
    print(f"\n--- Converting Single File ---")
    print(f"Input:  {file_path}")
    print(f"Output: {output_wav_path}")
    print("-" * 30)
    run_ffmpeg_conversion(file_path, output_wav_path)
    print("-" * 30)

def convert_directory(dir_path: Path):
    """
    Handles batch conversion of all audio files in a directory.
    Outputs are saved to a 'converted_to_wav' subdirectory.
    """
    output_subdir_name = "converted_to_wav"
    output_dir = dir_path / output_subdir_name

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"❌ Error: Could not create output directory '{output_dir}': {e}")
        return

    print(f"\n--- Batch Converting Directory ---")
    print(f"Source:      {dir_path}")
    print(f"Destination: {output_dir}")
    print("-" * 30)

    files_to_process = [
        p for p in dir_path.rglob('*')
        if p.is_file() and (p.name.lower().endswith('.mp3') or p.name.lower().endswith('.m4a'))
    ]

    if not files_to_process:
        print("ℹ️ No .mp3 or .m4a files found in the source directory.")
        return

    success_count = 0
    for i, audio_file_path in enumerate(files_to_process, 1):
        print(f"Processing file {i} of {len(files_to_process)}: {audio_file_path.name}")
        output_wav_path = output_dir / audio_file_path.with_suffix('.wav').name
        if run_ffmpeg_conversion(audio_file_path, output_wav_path):
            success_count += 1

    print("-" * 30)
    print(f"Batch conversion complete. {success_count}/{len(files_to_process)} files converted successfully.")

if __name__ == "__main__":
    if not check_ffmpeg():
        exit(1)

    parser = argparse.ArgumentParser(
        description="Convert .mp3 or .m4a audio files to .wav format (16kHz, mono).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_path",
        help="Path to a single audio file or a directory of audio files to convert."
    )
    args = parser.parse_args()

    input_path = Path(args.input_path).resolve()

    if not input_path.exists():
        print(f"❌ Error: The specified path does not exist: {input_path}")
        exit(1)

    if input_path.is_file():
        convert_single_file(input_path)
    elif input_path.is_dir():
        convert_directory(input_path)
    else:
        print(f"❌ Error: The specified path is not a valid file or directory: {input_path}")
        exit(1)

