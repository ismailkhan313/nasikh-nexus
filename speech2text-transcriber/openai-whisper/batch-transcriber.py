#!/usr/bin/env python3
# flake8: noqa

from openai import OpenAI # type: ignore
import os
import shutil # For deleting temporary directory
from pydub import AudioSegment # type: ignore
from pydub.exceptions import CouldntDecodeError # type: ignore
import traceback # For detailed error printing
# Removed: from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime # For timestamped folder names

# --- Configuration ---
client = OpenAI() # API key from OPENAI_API_KEY env variable

# Base directory for all transcription outputs. Run-specific folders will be created inside this.
FINAL_TXT_OUTPUT_BASE_DIRECTORY = "/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions/"
# Base directory for temporary audio chunks
TEMP_CHUNK_BASE_DIRECTORY = "/Users/viz1er/Documents/audio-lectures/temp-audio-chunks/"

MAX_SIZE_BYTES = 24 * 1024 * 1024  # 24 MB (OpenAI limit is 25MB)
CHUNK_DURATION_MINUTES = 15 # Duration of each main audio chunk
OVERLAP_SECONDS = 10        # Overlap between chunks in seconds
CHUNK_DURATION_MS = CHUNK_DURATION_MINUTES * 60 * 1000
OVERLAP_MS = OVERLAP_SECONDS * 1000

# Removed: MAX_CONCURRENT_CHUNK_TRANSCRIPTIONS

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

SUPPORTED_AUDIO_EXTENSIONS = ['.m4a', '.mp3', '.wav', '.mpga', '.mpeg', '.webm', '.aac', '.ogg', '.flac']
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
        print(f"    Error transcribing chunk {os.path.basename(file_path_to_transcribe)}: {e}")
        return None

def process_single_audio_file(audio_file_path, current_run_output_dir):
    """
    Processes a single audio file: splits if necessary, transcribes sequentially,
    and saves the output to the specified run directory. Returns True on success, False on failure.
    """
    print(f"  Processing audio file: {audio_file_path}")

    files_to_process_paths = []
    current_file_temp_chunk_dir = None
    transcription_results = [] # Results will be collected sequentially

    try:
        file_size = os.path.getsize(audio_file_path)
        original_file_basename = os.path.basename(audio_file_path)
        sanitized_basename = os.path.splitext(original_file_basename)[0]
        # Sanitize for temp folder name
        sanitized_basename_for_temp_dir = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in sanitized_basename).rstrip()
        sanitized_basename_for_temp_dir = sanitized_basename_for_temp_dir.replace(" ", "_")


        if file_size > MAX_SIZE_BYTES:
            print(f"    File '{original_file_basename}' ({(file_size / (1024*1024)):.2f}MB) exceeds limit. Splitting...")

            unique_temp_subdir_name = f"chunks_for_{sanitized_basename_for_temp_dir}_{datetime.now().strftime('%H%M%S%f')}"
            current_file_temp_chunk_dir = os.path.join(TEMP_CHUNK_BASE_DIRECTORY, unique_temp_subdir_name)

            if os.path.exists(current_file_temp_chunk_dir):
                shutil.rmtree(current_file_temp_chunk_dir)
            os.makedirs(current_file_temp_chunk_dir)
            print(f"    Storing temporary chunks for this run in: {current_file_temp_chunk_dir}")

            try:
                audio = AudioSegment.from_file(audio_file_path)
            except CouldntDecodeError:
                print(f"    Error: Could not decode audio file: {audio_file_path}. Ensure ffmpeg is installed.")
                return False
            except Exception as e:
                print(f"    Error loading audio file with pydub: {e}")
                return False

            effective_step_ms = CHUNK_DURATION_MS - OVERLAP_MS
            audio_len_ms = len(audio)
            current_segment_start_ms = 0
            chunk_index = 0

            while current_segment_start_ms < audio_len_ms:
                chunk_actual_end_ms = min(current_segment_start_ms + CHUNK_DURATION_MS, audio_len_ms)
                chunk_audio_segment = audio[current_segment_start_ms : chunk_actual_end_ms]
                _, original_ext = os.path.splitext(original_file_basename)
                if not original_ext: original_ext = ".m4a"
                export_format = "mp4" if original_ext.lower() == ".m4a" else original_ext[1:]
                chunk_file_name = f"chunk_{chunk_index + 1}{original_ext}"
                chunk_file_path = os.path.join(current_file_temp_chunk_dir, chunk_file_name)

                print(f"      Exporting chunk {chunk_index + 1} ({current_segment_start_ms/1000:.1f}s to {chunk_actual_end_ms/1000:.1f}s)...")
                try:
                    chunk_audio_segment.export(chunk_file_path, format=export_format)
                    if os.path.getsize(chunk_file_path) > MAX_SIZE_BYTES:
                         print(f"      WARNING: Exported chunk '{chunk_file_name}' is still ({os.path.getsize(chunk_file_path)/(1024*1024):.2f}MB).")
                    files_to_process_paths.append(chunk_file_path)
                except Exception as e:
                    print(f"      Error exporting chunk {chunk_file_name}: {e}")
                chunk_index += 1
                if chunk_actual_end_ms == audio_len_ms: break
                current_segment_start_ms += effective_step_ms
                if current_segment_start_ms + OVERLAP_MS >= audio_len_ms and audio_len_ms - current_segment_start_ms < OVERLAP_MS :
                    if current_segment_start_ms < chunk_actual_end_ms - OVERLAP_MS :
                         current_segment_start_ms = chunk_actual_end_ms - OVERLAP_MS
                    else: break
            if not files_to_process_paths:
                print("    No chunks were created. Skipping file.")
                return False
            print(f"    Audio splitting complete. {len(files_to_process_paths)} chunks created.")
        else:
            print(f"    File '{original_file_basename}' ({(file_size / (1024*1024)):.2f}MB) is within size limit. Processing directly.")
            files_to_process_paths.append(audio_file_path)

        if not files_to_process_paths:
            print("    No audio segments to process for this file.")
            return False

        total_segments_to_transcribe = len(files_to_process_paths)
        print(f"    Starting sequential transcription for {total_segments_to_transcribe} segment(s)...")

        for idx, f_path in enumerate(files_to_process_paths):
            segment_name = os.path.basename(f_path)
            print(f"      Processing segment {idx + 1}/{total_segments_to_transcribe}: {segment_name}...")
            transcription_response = transcribe_audio_chunk_with_timestamps(f_path, TRANSCRIPTION_PROMPT)
            if transcription_response:
                transcription_results.append(transcription_response)
                print(f"        Successfully transcribed segment {idx + 1}/{total_segments_to_transcribe}: {segment_name}")
            else:
                # Error already printed by transcribe_audio_chunk_with_timestamps
                print(f"        Skipping transcription for segment {idx + 1}/{total_segments_to_transcribe} ({segment_name}) due to error.")


        if not transcription_results:
            print("    No transcription could be generated for this file (all segments failed or yielded no data).")
            return False

        all_words_to_combine = []
        min_word_start_time_in_chunk_s_for_overlap = OVERLAP_MS / 1000.0

        for idx, result_data in enumerate(transcription_results):
            words_in_chunk = []
            if hasattr(result_data, 'words') and isinstance(result_data.words, list):
                words_in_chunk = result_data.words
            elif hasattr(result_data, 'text'):
                 print(f"      Note: Segment {idx+1} has text but no word timestamps. Using full text.")
                 if idx == 0:
                     all_words_to_combine.extend(result_data.text.split())
                 else:
                     print(f"      Appending full text for segment {idx+1} due to missing word timestamps. Overlap handling will be imperfect.")
                     all_words_to_combine.extend(result_data.text.split())
                 continue

            if not words_in_chunk:
                print(f"      No words found in transcription data for segment {idx + 1}.")
                if not hasattr(result_data, 'text') or not result_data.text:
                    print(f"      Segment {idx+1} text is also empty.")
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
                    print(f"      Note: All words in segment {idx+1} were within the {OVERLAP_SECONDS}s overlap period and were filtered.")

        final_transcription = " ".join(all_words_to_combine).strip()
        final_transcription = " ".join(final_transcription.split())

        output_file_name = f"{os.path.splitext(original_file_basename)[0]}.txt"
        final_txt_output_file_path = os.path.join(current_run_output_dir, output_file_name)

        with open(final_txt_output_file_path, "w", encoding='utf-8') as text_file:
            text_file.write(final_transcription)
        print(f"    Successfully transcribed. Output saved to: {final_txt_output_file_path}")
        return True

    except FileNotFoundError:
        print(f"    Error: Audio file '{audio_file_path}' not found during processing.")
        return False
    except CouldntDecodeError:
        print(f"    Error: Could not decode audio file '{audio_file_path}'. Ensure ffmpeg is installed.")
        return False
    except Exception as e:
        print(f"    An unexpected error occurred processing {audio_file_path}: {e}")
        traceback.print_exc()
        return False
    finally:
        if current_file_temp_chunk_dir and os.path.exists(current_file_temp_chunk_dir):
            try:
                shutil.rmtree(current_file_temp_chunk_dir)
            except Exception as e:
                print(f"    Error cleaning up temporary directory {current_file_temp_chunk_dir}: {e}")

def batch_main():
    print("Batch Audio Transcription Script")
    print("=" * 30)
    print(f"IMPORTANT: This script requires 'pydub' (pip install pydub) and 'ffmpeg'.")
    print(f"Ensure ffmpeg is installed and in your system's PATH.\n")
    print(f"Settings: Chunk Duration: {CHUNK_DURATION_MINUTES} mins, Overlap: {OVERLAP_SECONDS} secs")
    # Removed: Max Concurrent Chunk Transcriptions print
    print(f"Temporary Chunks Location: {TEMP_CHUNK_BASE_DIRECTORY}")
    print(f"Base TXT Output Location: {FINAL_TXT_OUTPUT_BASE_DIRECTORY}")
    print(f"Using Transcription Prompt: \"{TRANSCRIPTION_PROMPT[:100]}...\" \n")

    if OVERLAP_MS >= CHUNK_DURATION_MS:
        print("Error: Overlap duration must be less than chunk duration. Exiting.")
        return

    try:
        if not os.path.exists(TEMP_CHUNK_BASE_DIRECTORY):
            os.makedirs(TEMP_CHUNK_BASE_DIRECTORY)
            print(f"Created base temporary chunk directory: {TEMP_CHUNK_BASE_DIRECTORY}")
    except OSError as e:
        print(f"CRITICAL Error creating base temporary chunk directory {TEMP_CHUNK_BASE_DIRECTORY}: {e}. Exiting.")
        return

    folder_path = input("Please enter the full path to the folder containing audio files: ")

    if not os.path.isdir(folder_path):
        print(f"Error: The path '{folder_path}' is not a valid directory. Exiting.")
        return

    source_folder_name = os.path.basename(os.path.normpath(folder_path))
    sanitized_run_folder_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in source_folder_name).rstrip().replace(" ", "_")
    if not sanitized_run_folder_name:
        sanitized_run_folder_name = f"transcription_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    run_specific_output_dir = os.path.join(FINAL_TXT_OUTPUT_BASE_DIRECTORY, sanitized_run_folder_name)
    print(f"Output for this run will be saved in: {run_specific_output_dir}")

    try:
        if not os.path.exists(FINAL_TXT_OUTPUT_BASE_DIRECTORY):
            os.makedirs(FINAL_TXT_OUTPUT_BASE_DIRECTORY)
            print(f"Created base final TXT output directory: {FINAL_TXT_OUTPUT_BASE_DIRECTORY}")
    except OSError as e:
        print(f"CRITICAL Error creating base final TXT output directory {FINAL_TXT_OUTPUT_BASE_DIRECTORY}: {e}. Exiting.")
        return

    try:
        if not os.path.exists(run_specific_output_dir):
            os.makedirs(run_specific_output_dir)
            print(f"Created run-specific output directory: {run_specific_output_dir}")
        else:
            print(f"Run-specific output directory already exists: {run_specific_output_dir}. Files may be overwritten or added.")
    except OSError as e:
        print(f"CRITICAL Error creating run-specific output directory {run_specific_output_dir}: {e}. Exiting.")
        return

    print(f"\nScanning folder: {folder_path}")
    audio_files_to_process = []
    for item in os.listdir(folder_path):
        full_item_path = os.path.join(folder_path, item)
        if os.path.isfile(full_item_path):
            file_ext = os.path.splitext(item)[1].lower()
            if file_ext in SUPPORTED_AUDIO_EXTENSIONS:
                audio_files_to_process.append(full_item_path)

    if not audio_files_to_process:
        print("No supported audio files found in the specified folder. Exiting.")
        return

    total_files = len(audio_files_to_process)
    print(f"Found {total_files} audio file(s) to process: {', '.join(os.path.basename(p) for p in audio_files_to_process)}")
    print("-" * 30)

    successful_transcriptions = 0
    failed_transcriptions = 0

    for i, audio_path in enumerate(audio_files_to_process):
        print(f"\nProcessing file {i + 1} of {total_files}: {os.path.basename(audio_path)}")
        print("-" * 20)
        try:
            if process_single_audio_file(audio_path, run_specific_output_dir):
                successful_transcriptions += 1
            else:
                failed_transcriptions += 1
        except Exception as e:
            print(f"  UNHANDLED EXCEPTION during processing of {os.path.basename(audio_path)}: {e}")
            traceback.print_exc()
            failed_transcriptions +=1
        print("-" * 20)

    print("\nBatch Processing Summary:")
    print("=" * 30)
    print(f"Total files processed: {total_files}")
    print(f"Successfully transcribed: {successful_transcriptions}")
    print(f"Failed transcriptions: {failed_transcriptions}")
    print(f"Output for this run is in: {run_specific_output_dir}")
    print("=" * 30)

if __name__ == "__main__":
    batch_main()