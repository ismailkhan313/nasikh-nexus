This folder essentially holds utility scripts for whisper.cpp for use on my macbook m1 pro.

The python files

Workflow:

1. Convert mp3 or m4a files to .wav by using `batch-convert-to-wav.py`
2. Run the transcribe scripts using whisper.cpp
3. Delete all .wav files from audio lecture directory with `delete-wav-files.py`. This needs to be done because wav files are insanely large.

More to come...
