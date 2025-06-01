#!/bin/bash

# Script to batch delete .wav files in a specified directory and its subdirectories.

# Prompt for the target directory
read -r -p "Enter the path to the directory FROM WHICH you want to delete all .wav files: " TARGET_DIR

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

echo ""
echo "WARNING: This script will search for and delete ALL .wav files"
echo "within the directory '$TARGET_DIR' and all its subdirectories."
echo "This action is IRREVERSIBLE."
echo ""

# Confirmation prompt
read -r -p "Are you absolutely sure you want to proceed? (yes/no): " CONFIRMATION

if [[ "$CONFIRMATION" != "yes" ]]; then
  echo "Operation cancelled by the user."
  exit 0
fi

echo ""
echo "Searching for .wav files in '$TARGET_DIR' to delete..."
echo "-----------------------------------------------------"

deleted_count=0
found_files=0

# Use find to locate .wav files, then loop through them for individual deletion and counting
# -type f : Only find regular files
# -iname : Case-insensitive name matching for extensions
# -print0 and while IFS= read -r -d $'\0': Robust way to handle filenames with spaces, newlines, etc.
find "$TARGET_DIR" -type f -iname "*.wav" -print0 | while IFS= read -r -d $'\0' wav_file; do
  ((found_files++))
  echo "Deleting: $wav_file"
  rm -f "$wav_file" # -f forces deletion without prompting for each file and suppresses errors if a file cannot be found (though find should ensure it exists)
  if [ $? -eq 0 ]; then
    ((deleted_count++))
    # echo "Successfully deleted: $wav_file" # Uncomment for more verbose output
  else
    echo "Error deleting '$wav_file'."
  fi
done

echo "-----------------------------------------------------"
echo ""

if [ "$found_files" -eq 0 ]; then
  echo "No .wav files found to delete in '$TARGET_DIR'."
else
  echo "Deletion process finished."
  echo "Found $found_files .wav file(s)."
  echo "Successfully deleted $deleted_count .wav file(s)."
  if [ "$deleted_count" -lt "$found_files" ]; then
    echo "Some files may not have been deleted due to errors."
  fi
fi

exit 0
