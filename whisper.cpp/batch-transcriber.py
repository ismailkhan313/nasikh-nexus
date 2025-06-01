#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
from pathlib import Path # For easier path manipulation

# --- Configuration ---
whisper_cpp_executable = "/Users/viz1er/Codebase/whisper.cpp/main"
model_path = "/Users/viz1er/Codebase/whisper.cpp/models/ggml-large-v3-turbo.bin"
# This is now the PARENT directory where batch-specific folders will be created
base_transcripts_parent_dir = Path("/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions")

# --- Thread and Processor Configuration ---
num_threads = "8"
num_processors = "2"

def main():
    # --- Ensure the PARENT output directory exists ---
    try:
        base_transcripts_parent_dir.mkdir(parents=True, exist_ok=True)
        print(f"Base directory for all transcript batches: {base_transcripts_parent_dir}")
    except OSError as e:
        print(f"Error: Could not create base output directory '{base_transcripts_parent_dir}': {e}")
        return

    # --- Get input FOLDER from user ---
    input_folder_str = input("Enter the full path to the folder containing your WAV audio files: ").strip()

    # --- Validate input folder ---
    if not input_folder_str:
        print("Error: No input folder path provided.")
        return

    input_folder_path = Path(input_folder_str).resolve() # Resolve to absolute path

    if not input_folder_path.is_dir():
        print(f"Error: Input folder not found or is not a directory: {input_folder_path}")
        return

    # --- Create a new subfolder for this specific batch run ---
    # The subfolder will be named after the input folder
    current_batch_output_dir = base_transcripts_parent_dir / input_folder_path.name
    try:
        current_batch_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Transcripts for this batch will be saved in: {current_batch_output_dir}")
    except OSError as e:
        print(f"Error: Could not create specific batch output directory '{current_batch_output_dir}': {e}")
        return

    # --- Find WAV files in the folder ---
    wav_files = list(input_folder_path.glob('*.wav'))

    if not wav_files:
        print(f"No .wav files found in '{input_folder_path}'.")
        return

    print(f"\nFound {len(wav_files)} .wav file(s) to process in '{input_folder_path}'.")
    total_files = len(wav_files)
    processed_count = 0
    success_count = 0
    error_count = 0

    for i, input_wav_file_path in enumerate(wav_files):
        processed_count += 1
        print(f"\n--- Processing file {processed_count}/{total_files}: {input_wav_file_path.name} ---")

        # --- Determine output file base name (within the current batch's output directory) ---
        output_file_base = current_batch_output_dir / input_wav_file_path.stem

        # --- Construct the command ---
        command = [
            str(whisper_cpp_executable),
            "-m", str(model_path),
            "-l", "auto",
            "-otxt",
            "-pp",  # Print progress
            "-t", num_threads,
            "-p", num_processors,
            "-f", str(input_wav_file_path),
            "-of", str(output_file_base)
        ]

        print(f"Output text file will be: {output_file_base}.txt")
        print(f"Using {num_threads} threads and {num_processors} processors.")
        print("-" * 30)

        try:
            process = subprocess.run(command, check=True, text=True)
            print("-" * 30)
            print(f"Transcription successful for: {input_wav_file_path.name}")
            print(f"Transcription saved to: {output_file_base}.txt")
            success_count += 1

        except subprocess.CalledProcessError as e:
            error_count += 1
            print("-" * 30)
            print(f"Error during transcription for file: {input_wav_file_path.name}")
            print(f"Return code: {e.returncode}")
            print("Error messages from whisper.cpp should have been printed above.")
        except FileNotFoundError:
            error_count += 1
            print(f"Critical Error: The whisper.cpp executable was not found at {whisper_cpp_executable}")
            print("Please check the path. Aborting batch processing.")
            break
        except Exception as e_global:
            error_count += 1
            print(f"An unexpected error occurred while processing {input_wav_file_path.name}: {e_global}")

    print("\n--- Batch Processing Summary ---")
    print(f"Total files found: {total_files}")
    print(f"Successfully transcribed: {success_count}")
    print(f"Failed to transcribe: {error_count}")
    print(f"Transcripts for this batch are located in: {current_batch_output_dir}")

if __name__ == "__main__":
    main()