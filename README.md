# Nasikh Nexus

In Arabic, Nasikh (ناسخ) is the active participle of the verb nasakha (نسخ), which means "to copy," "to transcribe," or "to write down." A Nasikh is literally a "scribe," "copier," or "transcriber."

A "nexus" is a central point or a connection that links two or more things. It signifies a core, a hub, or a focal point where different elements converge. In other words, Nasikh Nexus can translated to The Scribe's Hub or The Central Point of Transcription. It implies this project is the central connection point for all scribal tasks, seamlessly handling both the auditory and visual-to-text conversion.

Nasikh Nexus is a powerful toolkit designed for processing classical Arabic content into English. This tool leverages current open-source AI models to do two things:

1. Produce highly accurate audio transcription of bilingual audio in Arabic and English, and Arabic only audio.
2. Produce complete and accurate OCR for scanned documents in Arabic and English and potentially classical Arabic manuscripts.

The project integrates Whisper.cpp for robust speech-to-text and Mistral AI for precise OCR on Arabic texts.

## ✨ Features

1. YouTube Audio Downloader: Directly download audio from YouTube videos for transcription leveraging the `yt-dlp` and `ffmpeg` packages.

2. Other web scrapers and downloaders. Specifically, downloaders for the online digital arabic manuscript repository Turath.io

3. Whisper Transcription: High-accuracy, timestamped audio transcription primarily optimized for English lectures with Arabic included. Primarily leverage the popular open-source `whisper.cpp` repository for MacOS.

4. Mistral OCR: Extract text from Arabic PDFs and images of manuscripts with high precision using their free and paid models.

5. Modular & Organized: A clean, scalable project structure that separates concerns and is easy to maintain.
