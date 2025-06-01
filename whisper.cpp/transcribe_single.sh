#!/bin/bash

# --- Configuration ---
WHISPER_CPP_EXECUTABLE="./main" # Path to your whisper.cpp main executable
MODEL_PATH="models/ggml-large-v3-turbo.bin" # Path to your model file
OUTPUT_TRANSCRIPTION_DIR="/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions"

# --- Ensure output directory exists ---
mkdir -p "$OUTPUT_TRANSCRIPTION_DIR"
if [ ! -d "$OUTPUT_TRANSCRIPTION_DIR" ]; then
  echo "Error: Could not create or find output directory: $OUTPUT_TRANSCRIPTION_DIR"
  exit 1
fi

# --- Get input WAV file from user ---
read -r -p "Enter the full path to the WAV audio file: " INPUT_WAV_FILE

# --- Validate input file ---
if [ -z "$INPUT_WAV_FILE" ]; then
  echo "Error: No input file provided."
  exit 1
fi

if [ ! -f "$INPUT_WAV_FILE" ]; then
  echo "Error: Input file not found at: $INPUT_WAV_FILE"
  exit 1
fi

# --- Get the base name of the audio file (e.g., "output_audio_file" from ".../output_audio_file.wav") ---
BASENAME_NO_EXT=$(basename "$INPUT_WAV_FILE" .wav)

# --- Define the base for the output file path (whisper.cpp will add .txt) ---
OUTPUT_FILE_BASE="$OUTPUT_TRANSCRIPTION_DIR/$BASENAME_NO_EXT"
RAW_OUTPUT_TXT_FILE="$OUTPUT_FILE_BASE.txt"
PARAGRAPH_OUTPUT_TXT_FILE="$OUTPUT_FILE_BASE_paragraph.txt" # Optional: new file for paragraph version

# --- Construct and run the whisper.cpp command ---
echo ""
echo "Processing: $INPUT_WAV_FILE"
echo "Model: $MODEL_PATH"
echo "Raw output will be saved as: $RAW_OUTPUT_TXT_FILE"
echo ""

"$WHISPER_CPP_EXECUTABLE" -m "$MODEL_PATH" -l auto -otxt -f "$INPUT_WAV_FILE" -of "$OUTPUT_FILE_BASE"

# --- Check exit status ---
if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Transcription successful!"
  echo "Raw output saved to: $RAW_OUTPUT_TXT_FILE"

  # --- Post-process to create a single paragraph ---
  echo "Converting to single paragraph format..."
  # Replace newlines with spaces, then squeeze multiple spaces into one
  tr '\n' ' ' < "$RAW_OUTPUT_TXT_FILE" | tr -s ' ' > "$PARAGRAPH_OUTPUT_TXT_FILE"
  # If you want to overwrite the original file instead (use with caution):
  # tr '\n' ' ' < "$RAW_OUTPUT_TXT_FILE" | tr -s ' ' > temp_file.txt && mv temp_file.txt "$RAW_OUTPUT_TXT_FILE"


  echo "Paragraph version saved to: $PARAGRAPH_OUTPUT_TXT_FILE"
  # If overwriting, you'd say: echo "Formatted as single paragraph in: $RAW_OUTPUT_TXT_FILE"

else
  echo ""
  echo "❌ Error during transcription."
fi

exit 0