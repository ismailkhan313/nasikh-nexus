#!/usr/bin/env python3
# flake8: noqa

from openai import OpenAI # type: ignore
import os
import shutil # For deleting temporary directory
from pydub import AudioSegment # type: ignore
from pydub.exceptions import CouldntDecodeError # type: ignore
import traceback # For detailed error printing

# --- Configuration ---
client = OpenAI() # API key from OPENAI_API_KEY env variable

# Final .txt output directory
FINAL_TXT_OUTPUT_DIRECTORY = "/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions/"

# --- !!! NEW: Base directory for temporary audio chunks !!! ---
TEMP_CHUNK_BASE_DIRECTORY = "/Users/viz1er/Documents/audio-lectures/temp-audio-chunks/"

MAX_SIZE_BYTES = 24 * 1024 * 1024  # 24 MB (OpenAI limit is 25MB)

CHUNK_DURATION_MINUTES = 15 # Duration of each main audio chunk
OVERLAP_SECONDS = 10        # Overlap between chunks in seconds

CHUNK_DURATION_MS = CHUNK_DURATION_MINUTES * 60 * 1000
OVERLAP_MS = OVERLAP_SECONDS * 1000

TRANSCRIPTION_PROMPT = (
    "This audio is an English lecture that includes some Arabic words, phrases, or short quotes. Please adhere to the following transcription guidelines:\n\n"
    "1.  **Primary Language:** The transcript should be predominantly in English.\n"
    "2.  **Arabic Script:** Transcribe all spoken Arabic words and phrases using Arabic script (e.g., 'اَلْعَرَبِيَّةُ', not 'al-arabiyyah' or transliterated forms).\n"
    "3.  **No Translation:** Do NOT translate Arabic speech into English, or English speech into Arabic. The original language used for any given word or phrase must be preserved in the transcript.\n"
    "4.  **Integration:** Arabic quotes or phrases should be embedded naturally within the English transcript, reflecting how they were spoken in the lecture.\n\n"
    "**Example of desired output:**\n\n"
    "...the speaker emphasized the importance of 'اَلصَّبْرُ' in this context. He then elaborated on its meaning in English...\n\n"
    "or\n\n"
    "...he began the quote by saying, 'قَالَ ٱللهُ تَعَالَىٰ', and then proceeded with the verse...\n\n"
    "**Contextual Information to Assist Transcription:**\n"
    "* The Arabic is typically for short quotations from source texts or key terms followed by explanation in English.\n"
    "* The main body of the lecture and explanations will be in English.\n\n"
    "Ensure the final transcript accurately reflects both the English and Arabic content as spoken, with Arabic rendered in its native script."
)

# --- End Configuration ---

def transcribe_audio_chunk_with_timestamps(file_path_to_transcribe, prompt_text):
    """
    Transcribes a single audio chunk using a prompt and returns the full
    verbose_json object which includes word timestamps.
    """
    try:
        with open(file_path_to_transcribe, "rb") as audio_chunk_file:
            transcription_obj = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_chunk_file,
                response_format="verbose_json",
                timestamp_granularities=["word"],
                prompt=prompt_text
            )
        return transcription_obj
    except Exception as e:
        print(f"Error transcribing chunk {os.path.basename(file_path_to_transcribe)}: {e}")
        return None

def main():
    print("Audio Transcription Script with Overlapping Chunks & Custom Prompt")
    print(f"IMPORTANT: This script requires 'pydub' (pip install pydub) and 'ffmpeg'.")
    print(f"Ensure ffmpeg is installed and in your system's PATH.\n")
    print(f"Settings: Chunk Duration: {CHUNK_DURATION_MINUTES} mins, Overlap: {OVERLAP_SECONDS} secs")
    print(f"Temporary Chunks Location: {TEMP_CHUNK_BASE_DIRECTORY}")
    print(f"Final TXT Output Location: {FINAL_TXT_OUTPUT_DIRECTORY}")
    print(f"Using Transcription Prompt: \"{TRANSCRIPTION_PROMPT[:100]}...\" \n")

    if OVERLAP_MS >= CHUNK_DURATION_MS:
        print("Error: Overlap duration must be less than chunk duration.")
        print(f"Overlap: {OVERLAP_SECONDS}s, Chunk Duration: {CHUNK_DURATION_MINUTES * 60}s")
        return

    audio_file_path = input("Please enter the full path to your audio file: ")

    # Ensure the FINAL .txt output directory exists
    try:
        if not os.path.exists(FINAL_TXT_OUTPUT_DIRECTORY):
            os.makedirs(FINAL_TXT_OUTPUT_DIRECTORY)
            print(f"Created final TXT output directory: {FINAL_TXT_OUTPUT_DIRECTORY}")
    except OSError as e:
        print(f"Error creating final TXT output directory {FINAL_TXT_OUTPUT_DIRECTORY}: {e}")
        return

    # Ensure the BASE temporary chunk directory exists
    try:
        if not os.path.exists(TEMP_CHUNK_BASE_DIRECTORY):
            os.makedirs(TEMP_CHUNK_BASE_DIRECTORY)
            print(f"Created base temporary chunk directory: {TEMP_CHUNK_BASE_DIRECTORY}")
    except OSError as e:
        print(f"Error creating base temporary chunk directory {TEMP_CHUNK_BASE_DIRECTORY}: {e}")
        return

    if not os.path.isfile(audio_file_path):
        print(f"Error: The audio file '{audio_file_path}' was not found.")
        return

    files_to_process_paths = []
    # This will be the specific subdirectory for the current audio file's chunks
    current_file_temp_chunk_dir = None
    transcription_results = []

    try:
        file_size = os.path.getsize(audio_file_path)
        original_file_basename = os.path.basename(audio_file_path)
        # Sanitize basename for directory creation (remove problematic characters)
        sanitized_basename = os.path.splitext(original_file_basename)[0]
        sanitized_basename = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in sanitized_basename).rstrip()
        sanitized_basename = sanitized_basename.replace(" ", "_")


        if file_size > MAX_SIZE_BYTES:
            print(f"File '{original_file_basename}' ({(file_size / (1024*1024)):.2f}MB) exceeds {MAX_SIZE_BYTES / (1024*1024):.0f}MB limit. Splitting into overlapping chunks...")

            # Create a unique subdirectory within the base temp directory for this specific audio file's chunks
            unique_temp_subdir_name = f"chunks_for_{sanitized_basename}"
            current_file_temp_chunk_dir = os.path.join(TEMP_CHUNK_BASE_DIRECTORY, unique_temp_subdir_name)

            if os.path.exists(current_file_temp_chunk_dir):
                shutil.rmtree(current_file_temp_chunk_dir) # Clean up previous temp dir for this specific file
            os.makedirs(current_file_temp_chunk_dir)
            print(f"Storing temporary chunks for this run in: {current_file_temp_chunk_dir}")


            try:
                audio = AudioSegment.from_file(audio_file_path)
            except CouldntDecodeError:
                print(f"Error: Could not decode audio file: {audio_file_path}.")
                print("Please ensure ffmpeg is installed and accessible in your system's PATH.")
                return
            except Exception as e:
                print(f"Error loading audio file with pydub: {e}")
                return

            effective_step_ms = CHUNK_DURATION_MS - OVERLAP_MS
            audio_len_ms = len(audio)
            current_segment_start_ms = 0
            chunk_index = 0

            while current_segment_start_ms < audio_len_ms:
                chunk_actual_end_ms = min(current_segment_start_ms + CHUNK_DURATION_MS, audio_len_ms)
                chunk_audio_segment = audio[current_segment_start_ms : chunk_actual_end_ms]

                _, original_ext = os.path.splitext(original_file_basename)
                if not original_ext: original_ext = ".m4a" # Default
                export_format = "mp4" if original_ext.lower() == ".m4a" else original_ext[1:]

                chunk_file_name = f"chunk_{chunk_index + 1}{original_ext}"
                chunk_file_path = os.path.join(current_file_temp_chunk_dir, chunk_file_name) # Use specific temp dir

                print(f"Exporting chunk {chunk_index + 1} ({current_segment_start_ms/1000:.1f}s to {chunk_actual_end_ms/1000:.1f}s): {chunk_file_path}...")
                try:
                    chunk_audio_segment.export(chunk_file_path, format=export_format)
                    if os.path.getsize(chunk_file_path) > MAX_SIZE_BYTES:
                         print(f"WARNING: Exported chunk '{chunk_file_name}' is still ({os.path.getsize(chunk_file_path)/(1024*1024):.2f}MB).")
                    files_to_process_paths.append(chunk_file_path)
                except Exception as e:
                    print(f"Error exporting chunk {chunk_file_name}: {e}. Make sure ffmpeg is installed correctly.")

                chunk_index += 1
                if chunk_actual_end_ms == audio_len_ms:
                    break
                current_segment_start_ms += effective_step_ms
                if current_segment_start_ms + OVERLAP_MS >= audio_len_ms and audio_len_ms - current_segment_start_ms < OVERLAP_MS :
                    if current_segment_start_ms < chunk_actual_end_ms :
                         current_segment_start_ms = chunk_actual_end_ms - OVERLAP_MS
                    else:
                         break
        else:
            print(f"File '{original_file_basename}' ({(file_size / (1024*1024)):.2f}MB) is within size limit. Processing directly.")
            files_to_process_paths.append(audio_file_path)

        total_files = len(files_to_process_paths)
        for idx, f_path in enumerate(files_to_process_paths):
            print(f"\nProcessing file {idx + 1}/{total_files}: {os.path.basename(f_path)}...")
            transcription_response = transcribe_audio_chunk_with_timestamps(f_path, TRANSCRIPTION_PROMPT)
            if transcription_response:
                transcription_results.append(transcription_response)
            else:
                print(f"Skipping transcription for {os.path.basename(f_path)} due to error.")

        if not transcription_results:
            print("No transcription could be generated.")
            return

        all_words_to_combine = []
        min_word_start_time_in_chunk_s_for_overlap = OVERLAP_MS / 1000.0

        for idx, result_data in enumerate(transcription_results):
            words_in_chunk = result_data.words if hasattr(result_data, 'words') and isinstance(result_data.words, list) else []

            if not words_in_chunk:
                print(f"No words found in transcription for chunk {idx + 1}.")
                if hasattr(result_data, 'text') and result_data.text:
                    if idx == 0:
                        all_words_to_combine.extend(result_data.text.split())
                        print(f"Chunk {idx+1} has text but no word timestamps. Adding full text as it's the first chunk.")
                    else:
                         print(f"Chunk {idx+1} has text but no word timestamps. Cannot reliably stitch. Text: '{result_data.text[:50]}...'")
                continue

            if idx == 0:
                for word_data in words_in_chunk:
                    all_words_to_combine.append(word_data.word)
            else:
                appended_word_for_chunk = False
                for word_data in words_in_chunk:
                    if word_data.start >= min_word_start_time_in_chunk_s_for_overlap:
                        all_words_to_combine.append(word_data.word)
                        appended_word_for_chunk = True
                if not appended_word_for_chunk and words_in_chunk:
                    print(f"Note: All words in chunk {idx+1} were within the overlap period. No new words added from this chunk.")

        final_transcription = " ".join(all_words_to_combine)

        # Output file path for the final .txt file (remains the same)
        file_name_without_ext = os.path.splitext(original_file_basename)[0]
        output_file_name = f"{file_name_without_ext}.txt"
        final_txt_output_file_path = os.path.join(FINAL_TXT_OUTPUT_DIRECTORY, output_file_name)

        with open(final_txt_output_file_path, "w", encoding='utf-8') as text_file:
            text_file.write(final_transcription)

        print(f"\nTranscription successful!")
        print(f"Output saved to: {final_txt_output_file_path}")

    except FileNotFoundError:
        print(f"Error: An audio file was not found during processing.")
    except CouldntDecodeError:
        print(f"Error: Could not decode audio file. Please ensure ffmpeg is installed and in PATH.")
    except Exception as e:
        print(f"An unexpected error occurred in main processing: {e}")
        traceback.print_exc()
    finally:
        # Clean up the specific temporary chunk directory for the processed file
        if current_file_temp_chunk_dir and os.path.exists(current_file_temp_chunk_dir):
            try:
                print(f"Cleaning up temporary chunk directory: {current_file_temp_chunk_dir}")
                shutil.rmtree(current_file_temp_chunk_dir)
            except Exception as e:
                print(f"Error cleaning up temporary directory {current_file_temp_chunk_dir}: {e}")

if __name__ == "__main__":
    main()