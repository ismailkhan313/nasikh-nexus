#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
from pathlib import Path # For easier path manipulation

# --- Configuration ---
whisper_cpp_executable = "/Users/viz1er/Codebase/whisper.cpp/main"
model_path = "/Users/viz1er/Codebase/whisper.cpp/models/ggml-large-v3-turbo.bin" # Assuming this model path is correct now
output_transcripts_dir = Path("/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions")

# --- NEW: Thread and Processor Configuration ---
num_threads = "8"  
num_processors = "2"

# --- Ensure output directory exists ---
try:
    output_transcripts_dir.mkdir(parents=True, exist_ok=True)
    print(f"Transcripts will be saved in: {output_transcripts_dir}")
except OSError as e:
    print(f"Error: Could not create output directory '{output_transcripts_dir}': {e}")
    exit(1)

# --- Get input WAV file from user ---
input_wav_file_str = input("Enter the full path to the WAV audio file: ").strip()

# --- Validate input file ---
if not input_wav_file_str:
    print("Error: No input file path provided.")
    exit(1)

input_wav_file_path = Path(input_wav_file_str)

if not input_wav_file_path.is_file():
    print(f"Error: Input file not found at: {input_wav_file_path}")
    exit(1)

if input_wav_file_path.suffix.lower() != ".wav":
    print(f"Warning: Input file '{input_wav_file_path.name}' does not have a .wav extension. Proceeding anyway.")

# --- Determine output file base name ---
output_file_base = output_transcripts_dir / input_wav_file_path.stem

# --- Construct the command ---
command = [
    str(whisper_cpp_executable),
    "-m", str(model_path),
    "-l", "auto",
    "-otxt",
    "-pp",  # Print progress
    "-t", num_threads,      # <--- ADDED for threads
    "-p", num_processors,   # <--- ADDED for processors
    "-f", str(input_wav_file_path),
    "-of", str(output_file_base)
]

print(f"\nInput audio file: {input_wav_file_path}")
print(f"Output text file will be: {output_file_base}.txt")
print(f"Using {num_threads} threads and {num_processors} processors.")
print(f"Executing command: {' '.join(command)}")
print("-" * 30)

try:
    # Run the command without capturing output to see live progress
    process = subprocess.run(command, check=True, text=True)

    print("-" * 30)
    print("\nTranscription successful!")
    print(f"Transcription saved to: {output_file_base}.txt")

except subprocess.CalledProcessError as e:
    print("-" * 30)
    print(f"Error during transcription with whisper.cpp:")
    print(f"Return code: {e.returncode}")
    print("Error messages from whisper.cpp should have been printed above.")
except FileNotFoundError:
    print(f"Error: The whisper.cpp executable was not found at {whisper_cpp_executable}")
    print("Please check the path.")
except Exception as e_global:
    print(f"An unexpected error occurred: {e_global}")