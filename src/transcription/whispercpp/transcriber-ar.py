#!/usr/bin/env python3
# flake8: noqa

import subprocess
import os
from pathlib import Path

# --- Configuration ---
whisper_cpp_executable = "/Users/viz1er/Codebase/whisper.cpp/main"
model_path = "/Users/viz1er/Codebase/whisper.cpp/models/ggml-large-v3-turbo.bin"
transcripts_output_dir = Path(
    "/Users/viz1er/Codebase/obsidian-vault/05 Projects/Nasikh Nexus - Transcription Automation/Transcriptions/Completed"
)

# --- Thread and Processor Configuration ---
num_threads = "8"
num_processors = "2"


def main():
    try:
        transcripts_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Transcripts will be saved in: {transcripts_output_dir}")
    except OSError as e:
        print(
            f"Error: Could not create output directory '{transcripts_output_dir}': {e}"
        )
        return

    input_path_str = input(
        "Enter the full path to a folder or a single .wav file: "
    ).strip()

    if not input_path_str:
        print("Error: No input path provided.")
        return

    input_path = Path(input_path_str).resolve()

    if not input_path.exists():
        print(f"Error: Input path not found: {input_path}")
        return

    wav_files = []
    if input_path.is_dir():
        print(f"Scanning folder: {input_path}")
        wav_files = list(input_path.glob("*.wav"))
    elif input_path.is_file() and input_path.suffix.lower() == ".wav":
        wav_files = [input_path]
    else:
        print(
            f"Error: The provided path is not a valid directory or .wav file: {input_path}"
        )
        return

    if not wav_files:
        print(f"No .wav files to process at the specified path: '{input_path}'.")
        return

    print(f"\nFound {len(wav_files)} .wav file(s) to process.")
    total_files = len(wav_files)
    success_count = 0
    error_count = 0
    skipped_count = 0

    caffeinate_command = ["caffeinate", "-s"]

    for i, input_wav_file_path in enumerate(wav_files):
        print(
            f"\n--- Checking file {i + 1}/{total_files}: {input_wav_file_path.name} ---"
        )

        output_file_base = transcripts_output_dir / input_wav_file_path.stem
        output_txt_file = Path(f"{output_file_base}.txt")

        if output_txt_file.exists():
            print(f"Transcript already exists: {output_txt_file}. Skipping.")
            skipped_count += 1
            continue

        print("Transcript does not exist. Starting transcription...")

        # --- FINAL ADVANCED COMMAND FOR HALLUCINATION CONTROL ---
        whisper_command = [
            str(whisper_cpp_executable),
            "-m",
            str(model_path),
            "-f",
            str(input_wav_file_path),
            "-of",
            str(output_file_base),
            "-l",
            "ar",
            "-t",
            num_threads,
            "-p",
            num_processors,
            "-otxt",
            "-nt",
            "-bs",
            "8",
            "--best-of",
            "5",
            # ADVANCED: Use thresholds to enable anti-hallucination fallbacks
            "--logprob-thold",
            "-0.8",
            "--entropy-thold",
            "2.6",
            # ADVANCED: Use a highly specific prompt to prevent code-switching
            "--prompt",
            "بسم الله الرحمن الرحيم. الحمد لله. هذا باب في النحو عن حروف العطف. الناسخ يدخل على الجملة الاسمية كالمبتدأ والخبر ويغير الإعراب. الكلام في هذا الدرس عن الصفة والإعراب والعطف بالواو والفاء ثم أو.",
        ]

        full_command = caffeinate_command + whisper_command

        print("Using advanced settings for hallucination control.")

        try:
            process = subprocess.run(
                full_command, check=True, text=True, capture_output=True
            )
            print("--- whisper.cpp output ---")
            print(process.stdout)
            print("--------------------------")
            print(f"Transcription process finished for: {input_wav_file_path.name}")
            print(f"Transcription file saved to: {output_txt_file}")
            success_count += 1

        except subprocess.CalledProcessError as e:
            error_count += 1
            print("--- ERROR ---")
            print(f"Error during transcription for file: {input_wav_file_path.name}")
            print(f"Return code: {e.returncode}")
            print(f"whisper.cpp stdout:\n{e.stdout}")
            print(f"whisper.cpp stderr:\n{e.stderr}")
        except FileNotFoundError:
            error_count += 1
            print(f"Critical Error: The command '{full_command[0]}' was not found.")
            break
        except Exception as e_global:
            error_count += 1
            print(f"An unexpected error occurred: {e_global}")

    print("\n--- Processing Summary ---")
    print(f"Total files checked: {total_files}")
    print(f"Successfully transcribed: {success_count}")
    print(f"Skipped (already exist): {skipped_count}")
    print(f"Failed to transcribe: {error_count}")
    print(f"All transcripts are located in: {transcripts_output_dir}")


if __name__ == "__main__":
    main()
