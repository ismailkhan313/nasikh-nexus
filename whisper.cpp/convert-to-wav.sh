#!/bin/bash

# Script to batch convert .mp3 and .m4a files to .wav format (16kHz, mono)
# using ffmpeg.

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
  echo "Error: ffmpeg is not installed. Please install ffmpeg to use this script."
  echo "On macOS, you can install it using Homebrew: brew install ffmpeg"
  echo "On Debian/Ubuntu, you can install it using: sudo apt update && sudo apt install ffmpeg"
  exit 1
fi

# Prompt for the target directory
read -r -p "Enter the path to the directory containing your audio files: " TARGET_DIR

# Check if the directory path is provided
if [ -z "$TARGET_DIR" ]; then
  echo "Error: No directory path provided."
  exit 1
fi

# Check if the provided path is a directory
if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: The path '$TARGET_DIR' is not a valid directory."
  exit 1
fi

# Define the output directory name for WAV files
OUTPUT_WAV_SUBDIR_NAME="converted_to_wav"
OUTPUT_WAV_DIR="$TARGET_DIR/$OUTPUT_WAV_SUBDIR_NAME"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_WAV_DIR"
if [ ! -d "$OUTPUT_WAV_DIR" ]; then
  echo "Error: Could not create output directory '$OUTPUT_WAV_DIR'."
  exit 1
fi

echo ""
echo "Searching for .mp3 and .m4a files in '$TARGET_DIR'..."
echo "(Excluding the output directory '$OUTPUT_WAV_DIR' itself)."
echo "Converted .wav files will be saved in '$OUTPUT_WAV_DIR'."
echo "-----------------------------------------------------"

processed_count=0

# Use find to locate mp3 and m4a files, then loop through them
# -path "$OUTPUT_WAV_DIR" -prune: Excludes the output directory from being searched
# -o : OR operator
# -type f : Only find regular files
# -iname : Case-insensitive name matching for extensions
# -print0 and while IFS= read -r -d $'\0': Robust way to handle filenames with spaces, newlines, etc.
find "$TARGET_DIR" -path "$OUTPUT_WAV_DIR" -prune -o -type f \( -iname "*.mp3" -o -iname "*.m4a" \) -print0 | while IFS= read -r -d $'\0' audio_file; do
  ((processed_count++))

  echo "Processing audio file ($processed_count): $audio_file"

  # Get the base name of the audio file (e.g., "song.mp3")
  base_name=$(basename "$audio_file")

  # Create the output WAV filename (e.g., "song.wav") by replacing the original extension
  output_wav_name="${base_name%.*}.wav"

  # Full path for the output WAV file
  output_wav_path="$OUTPUT_WAV_DIR/$output_wav_name"

  echo "Converting '$base_name' to '$output_wav_name'..."

  # Run ffmpeg for conversion:
  # -i "$audio_file": Input file
  # -ar 16000: Set audio sampling rate to 16kHz
  # -ac 1: Set number of audio channels to 1 (mono)
  # -c:a pcm_s16le: Set audio codec to PCM signed 16-bit little-endian (standard WAV format)
  # -loglevel error: Only show errors from ffmpeg, suppress verbose output unless there's an issue
  # -y: Overwrite output files without asking (if the WAV already exists in the output dir)
  ffmpeg -i "$audio_file" -ar 16000 -ac 1 -c:a pcm_s16le "$output_wav_path" -loglevel error -y

  if [ $? -eq 0 ]; then
    echo "Successfully converted to: $output_wav_path"
  else
    echo "Error converting '$base_name'. Check ffmpeg output if any (usually suppressed by -loglevel error)."
  fi
  echo "-----------------------------------------------------"
done

echo ""
if [ "$processed_count" -eq 0 ]; then
  echo "No .mp3 or .m4a files found to convert in '$TARGET_DIR' (excluding the output directory '$OUTPUT_WAV_DIR')."
else
  echo "Batch conversion finished. Processed $processed_count file(s)."
fi
echo "All converted .wav files are located in: $OUTPUT_WAV_DIR"

exit 0
