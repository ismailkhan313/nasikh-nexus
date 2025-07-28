#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
from pathlib import Path

# --- Configuration ---
whisper_cpp_executable = "/Users/viz1er/Codebase/whisper.cpp/main"
model_path = "/Users/viz1er/Codebase/whisper.cpp/models/ggml-large-v3-turbo.bin"
# This is now the single, consistent directory for all transcripts
transcripts_output_dir = Path(
    "/Users/viz1er/Codebase/obsidian-vault/05 Projects/Nasikh Nexus - OCR and Audio Transcription Automation/Transcriptions/Completed"
)

# --- Thread and Processor Configuration ---
num_threads = "8"
num_processors = "2"


def main():
    # --- Ensure the single, consistent output directory exists ---
    try:
        transcripts_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Transcripts will be saved in: {transcripts_output_dir}")
    except OSError as e:
        print(
            f"Error: Could not create output directory '{transcripts_output_dir}': {e}"
        )
        return

    # --- MODIFIED: Get input PATH from user (file or folder) ---
    input_path_str = input(
        "Enter the full path to a folder or a single .wav file: "
    ).strip()

    # --- Validate input path ---
    if not input_path_str:
        print("Error: No input path provided.")
        return

    input_path = Path(input_path_str).resolve()  # Resolve to absolute path

    if not input_path.exists():
        print(f"Error: Input path not found: {input_path}")
        return

    # --- MODIFIED: Collect WAV files from either a folder or a single file path ---
    wav_files = []
    if input_path.is_dir():
        # Path is a directory, find all .wav files inside
        print(f"Scanning folder: {input_path}")
        wav_files = list(input_path.glob("*.wav"))
    elif input_path.is_file():
        # Path is a file, check if it's a .wav file
        if input_path.suffix.lower() == ".wav":
            wav_files = [input_path]
        else:
            print(f"Error: The provided file is not a .wav file: {input_path}")
            return
    else:
        # Path is not a file or directory (e.g., a broken symlink)
        print(
            f"Error: The provided path is not a valid file or directory: {input_path}"
        )
        return

    # --- Check if any processable files were found ---
    if not wav_files:
        # This message is now more general
        print(f"No .wav files to process at the specified path: '{input_path}'.")
        return

    print(f"\nFound {len(wav_files)} .wav file(s) to process.")
    total_files = len(wav_files)
    processed_count = 0
    success_count = 0
    error_count = 0
    skipped_count = 0

    # --- Construct the caffeinate command wrapper ---
    # This ensures caffeinate is active for the entire duration of the script's core logic
    caffeinate_command = ["caffeinate", "-s"]

    # --- Loop through WAV files and process them ---
    # This loop works for both single and multiple files without modification
    for i, input_wav_file_path in enumerate(wav_files):
        processed_count += 1
        print(
            f"\n--- Checking file {processed_count}/{total_files}: {input_wav_file_path.name} ---"
        )

        # --- Determine output file path and check if it already exists ---
        output_file_base = transcripts_output_dir / input_wav_file_path.stem
        output_txt_file = Path(f"{output_file_base}.txt")

        # Check if the transcript already exists
        if output_txt_file.exists():
            print(f"Transcript already exists at: {output_txt_file}")
            print("Skipping transcription.")
            skipped_count += 1
            continue  # Move to the next file

        # --- Construct the whisper.cpp command ---
        print(f"Transcript does not exist. Starting transcription...")
        whisper_command = [
            str(whisper_cpp_executable),
            "-m",
            str(model_path),
            "-l",
            "auto",
            "-otxt",
            "-pp",
            "-t",
            num_threads,
            "-p",
            num_processors,
            "-f",
            str(input_wav_file_path),
            "-of",
            str(output_file_base),
        ]

        # Combine caffeinate with the whisper command
        full_command = caffeinate_command + whisper_command

        print(f"Output text file will be: {output_txt_file}")
        print(f"Using {num_threads} threads and {num_processors} processors.")
        print("-" * 30)

        try:
            # Use subprocess.run with the full command
            process = subprocess.run(
                full_command, check=True, text=True, capture_output=True
            )
            print("-" * 30)
            print(f"Transcription successful for: {input_wav_file_path.name}")
            print(f"Transcription saved to: {output_txt_file}")
            success_count += 1

        except subprocess.CalledProcessError as e:
            error_count += 1
            print("-" * 30)
            print(f"Error during transcription for file: {input_wav_file_path.name}")
            print(f"Return code: {e.returncode}")
            print(f"whisper.cpp stdout:\n{e.stdout}")
            print(f"whisper.cpp stderr:\n{e.stderr}")
        except FileNotFoundError:
            error_count += 1
            print(
                f"Critical Error: The whisper.cpp executable or caffeinate command was not found."
            )
            print(
                f"Please check the path for '{whisper_cpp_executable}' and ensure 'caffeinate' is available on your system."
            )
            print("Aborting processing.")
            break
        except Exception as e_global:
            error_count += 1
            print(
                f"An unexpected error occurred while processing {input_wav_file_path.name}: {e_global}"
            )

    # --- MODIFIED: More generic summary title ---
    print("\n--- Processing Summary ---")
    print(f"Total files checked: {total_files}")
    print(f"Successfully transcribed: {success_count}")
    print(f"Skipped (already exist): {skipped_count}")
    print(f"Failed to transcribe: {error_count}")
    print(f"All transcripts are located in: {transcripts_output_dir}")


if __name__ == "__main__":
    main()
