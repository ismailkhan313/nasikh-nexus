#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
from pathlib import Path # For easier path manipulation

# --- Configuration ---
whisper_cpp_executable = "/Users/viz1er/Codebase/whisper.cpp/main"
model_path = "/Users/viz1er/Codebase/whisper.cpp/models/ggml-large-v3-turbo.bin"
output_transcripts_dir = Path("/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions")

# --- Thread and Processor Configuration ---
num_threads = "8"
num_processors = "2"

def main():
    # --- Ensure output directory exists ---
    try:
        output_transcripts_dir.mkdir(parents=True, exist_ok=True)
        print(f"Transcripts will be saved in: {output_transcripts_dir}")
    except OSError as e:
        print(f"Error: Could not create output directory '{output_transcripts_dir}': {e}")
        return # Exit if we can't create the output directory

    # --- Get input FOLDER from user ---
    input_folder_str = input("Enter the full path to the folder containing your WAV audio files: ").strip()

    # --- Validate input folder ---
    if not input_folder_str:
        print("Error: No input folder path provided.")
        return

    input_folder_path = Path(input_folder_str)

    if not input_folder_path.is_dir():
        print(f"Error: Input folder not found or is not a directory: {input_folder_path}")
        return

    # --- Find WAV files in the folder ---
    wav_files = list(input_folder_path.glob('*.wav')) # Finds .wav files in the top-level directory

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

        # --- Determine output file base name ---
        output_file_base = output_transcripts_dir / input_wav_file_path.stem

        # --- Construct the command ---
        command = [
            str(whisper_cpp_executable),
            "-m", str(model_path),
            "-l", "auto",
            "-otxt",
            "-pp",  # Print progress
            "-t", num_threads,
            "-p", num_processors,
            "-f", str(input_wav_file_path), # Current WAV file in the loop
            "-of", str(output_file_base)    # Output base for this specific file
        ]

        print(f"Output text file will be: {output_file_base}.txt")
        print(f"Using {num_threads} threads and {num_processors} processors.")
        # print(f"Executing command: {' '.join(command)}") # Can be verbose for batch
        print("-" * 30)

        try:
            # Run the command without capturing output to see live progress
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
            error_count += 1 # This error would likely stop the whole batch if executable isn't found
            print(f"Critical Error: The whisper.cpp executable was not found at {whisper_cpp_executable}")
            print("Please check the path. Aborting batch processing.")
            break # Exit the loop if the main executable is missing
        except Exception as e_global:
            error_count += 1
            print(f"An unexpected error occurred while processing {input_wav_file_path.name}: {e_global}")

    print("\n--- Batch Processing Summary ---")
    print(f"Total files found: {total_files}")
    print(f"Successfully transcribed: {success_count}")
    print(f"Failed to transcribe: {error_count}")
    print(f"All transcripts saved in: {output_transcripts_dir}")

if __name__ == "__main__":
    main()