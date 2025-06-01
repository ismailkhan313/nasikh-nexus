#!/usr/bin/env python3
# flake8: noqa

import os
import requests
import argparse
import json
from dotenv import load_dotenv # For loading .env files

# ElevenLabs API Configuration
ELEVENLABS_API_ENDPOINT = "https://api.elevenlabs.io/v1/speech-to-text"
# Default model, 'scribe_v1'
DEFAULT_MODEL_ID = "scribe_v1" 

# Supported audio file extensions (add more if needed)
SUPPORTED_AUDIO_EXTENSIONS = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mpeg']

# --- Instructions for .env file ---
# 1. Make sure you have python-dotenv installed: pip install python-dotenv
# 2. Create a file named .env in the same directory as this script.
# 3. Add your API key to the .env file like this:
#    ELEVENLABS_API_KEY=your_actual_api_key_here
# ---

def transcribe_single_file(api_key, audio_file_path, model_id=DEFAULT_MODEL_ID):
    """
    Transcribes a single audio file using the ElevenLabs Scribe API.

    Args:
        api_key (str): Your ElevenLabs API key.
        audio_file_path (str): The path to the audio file.
        model_id (str): The model ID to use for transcription.

    Returns:
        str: The transcription text, or None if an error occurred.
    """
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}")
        return None

    headers = {
        "xi-api-key": api_key,
    }
    # Data payload for the API request
    # language_code has been removed to allow for auto-detection by the API
    data = {
        "model_id": model_id,
        "num_speakers": 1,       
        "tag_audio_events": False 
    }
    
    files_payload = None
    try:
        file_object = open(audio_file_path, "rb")
        files_payload = {
            "file": (os.path.basename(audio_file_path), file_object, "audio/mpeg") 
        }

        print(f"Transcribing {os.path.basename(audio_file_path)} using model {model_id} (language auto-detect), speakers: 1, audio_events: False...")
        response = requests.post(ELEVENLABS_API_ENDPOINT, headers=headers, data=data, files=files_payload, timeout=300) # Increased timeout, can be adjusted
        response.raise_for_status() 
        
        response_json = response.json()
        
        if "text" in response_json:
            return response_json["text"]
        else:
            print(f"Error: 'text' field not found in API response for {audio_file_path}.")
            print(f"API Response: {response.text}") 
            return None

    except requests.exceptions.RequestException as e:
        print(f"API Request Error for {audio_file_path}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Response Status Code: {e.response.status_code}")
            print(f"API Response Text: {e.response.text}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON response from API for {audio_file_path}.")
        if 'response' in locals(): 
             print(f"API Response (first 200 chars): {response.text[:200]}")
        return None
    except IOError as e:
        print(f"Error opening or reading file {audio_file_path}: {e}")
        return None
    finally:
        if files_payload and "file" in files_payload and files_payload["file"][1] and not files_payload["file"][1].closed:
            files_payload["file"][1].close()


def process_files(api_key, input_path, output_folder_path, model_id=DEFAULT_MODEL_ID):
    """
    Processes a single audio file or all audio files in a folder.
    """
    if not os.path.exists(output_folder_path):
        try:
            os.makedirs(output_folder_path)
            print(f"Created output folder: {output_folder_path}")
        except OSError as e:
            print(f"Error creating output folder {output_folder_path}: {e}")
            return

    if os.path.isfile(input_path):
        file_name, file_ext = os.path.splitext(os.path.basename(input_path))
        if file_ext.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
            print(f"Skipping non-audio file (or unsupported extension): {input_path}")
            return
        
        transcription = transcribe_single_file(api_key, input_path, model_id)
        if transcription:
            safe_file_name_base = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in file_name).rstrip()
            output_file_name = f"{safe_file_name_base}_transcription.txt"
            output_file_path = os.path.join(output_folder_path, output_file_name)
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(transcription)
                print(f"Transcription saved to: {output_file_path}")
            except IOError as e:
                print(f"Error saving transcription to {output_file_path}: {e}")

    elif os.path.isdir(input_path):
        print(f"Processing folder: {input_path}")
        for item in os.listdir(input_path):
            item_path = os.path.join(input_path, item)
            if os.path.isfile(item_path):
                file_name, file_ext = os.path.splitext(item)
                if file_ext.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                    transcription = transcribe_single_file(api_key, item_path, model_id)
                    if transcription:
                        safe_file_name_base = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in file_name).rstrip()
                        output_file_name = f"{safe_file_name_base}_transcription.txt"
                        output_file_path = os.path.join(output_folder_path, output_file_name)
                        try:
                            with open(output_file_path, "w", encoding="utf-8") as f:
                                f.write(transcription)
                            print(f"Transcription saved to: {output_file_path}")
                        except IOError as e:
                            print(f"Error saving transcription to {output_file_path}: {e}")
                else:
                    print(f"Skipping non-audio file (or unsupported extension): {item_path}")
            else:
                print(f"Skipping non-file item: {item_path}") 
    else:
        print(f"Error: Input path {input_path} is not a valid file or folder.")


if __name__ == "__main__":
    load_dotenv() 

    parser = argparse.ArgumentParser(description="Transcribe audio files using ElevenLabs Scribe API.")
    parser.add_argument("--model_id", help=f"ElevenLabs model ID for transcription (default: {DEFAULT_MODEL_ID}). Available: 'scribe_v1', 'scribe_v1_experimental'.", default=DEFAULT_MODEL_ID)
    
    args = parser.parse_args()

    api_key_to_use = os.getenv("ELEVENLABS_API_KEY")
    if not api_key_to_use:
        api_key_to_use = input("Please enter your ElevenLabs API key: ").strip()

    if not api_key_to_use:
        print("Error: API key is required.")
    else:
        input_path_from_user = input("Please enter the path to the audio file or folder: ").strip()
        if not input_path_from_user:
            print("Error: Input path is required.")
        else:
            input_path_expanded = os.path.expanduser(input_path_from_user)
            output_folder_path = "/Users/viz1er/Codebase/obsidian-vault/01 - Fleeting Notes/Transcriptions"
            
            process_files(api_key_to_use, input_path_expanded, output_folder_path, args.model_id)
            print("\nProcessing complete.")

