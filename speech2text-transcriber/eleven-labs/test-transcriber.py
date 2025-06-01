#!/usr/bin/env python3
# flake8: noqa

import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs # type: ignore

load_dotenv()

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

# Ask the user for the path to the audio file
audio_path = input("Please enter the path to your audio file: ")

# Check if the file exists
if not os.path.exists(audio_path):
    print(f"Error: The file '{audio_path}' was not found.")
    exit()

# Ask the user for the desired output .txt filename
output_txt_filename = input("Please enter the desired name for the output text file (e.g., transcript.txt): ")
# Ensure it ends with .txt
if not output_txt_filename.lower().endswith(".txt"):
    output_txt_filename += ".txt"

try:
    print("Processing audio file for transcription...")
    # Open the local audio file in binary read mode
    with open(audio_path, "rb") as audio_file:
        transcription_response = elevenlabs.speech_to_text.convert(
            file=audio_file,
            model_id="scribe_v1",  # Model to use
            # language_code is omitted to use the default (None for auto-detection)
            tag_audio_events=False,# Do not tag audio events
            diarize=True,          # Kept from original script
        )

    # The API response object has a 'text' attribute
    # containing the full transcript.
    transcript_text = transcription_response.text

    # Write the transcript text to the specified .txt file
    with open(output_txt_filename, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    print(f"Transcription complete. The transcript has been saved to: {output_txt_filename}")

except Exception as e:
    print(f"An error occurred: {e}")
    # You might want to print more detailed error information if it's an API error
    if hasattr(e, 'body'): # Check if the exception object has a 'body' attribute (common for HTTP errors from this SDK)
        print(f"Error details: {getattr(e, 'body')}")