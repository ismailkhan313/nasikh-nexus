import yt_dlp
import os
import sys

# --- Configuration ---
# Paste the full URL of the YouTube playlist here
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL_your_playlist_id_here"

# Name of the folder where transcripts will be saved
OUTPUT_FOLDER = "youtube_transcripts_manual"

# Desired language for the subtitles ('ar' for Arabic)
SUB_LANG = "ar"
# --- End of Configuration ---


def download_playlist_transcripts(playlist_url, output_dir, lang):
    os.makedirs(output_dir, exist_ok=True)
    print(f"📂 Saving transcripts to folder: '{output_dir}'")

    ydl_opts = {
        "ignoreerrors": True,
        # This is the key change: set to False to ignore auto-generated subs
        "writeautomaticsub": False,
        "writesubtitles": True,  # This enables downloading of manual subtitles
        "subtitleslangs": [lang],
        "skip_download": True,
        "convert_subtitles": "txt",
        "outtmpl": {"default": os.path.join(output_dir, "%(title)s.%(ext)s")},
    }

    if "PL_your_playlist_id_here" in playlist_url:
        sys.exit(
            "❌ Error: Please replace the placeholder PLAYLIST_URL with your actual YouTube playlist URL."
        )

    print(f"⏳ Starting download for playlist: {playlist_url}")
    print("ℹ️ Note: Only manually created transcripts will be downloaded.")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    print("\n✅ Script finished. Check the output folder for your transcripts.")


if __name__ == "__main__":
    download_playlist_transcripts(PLAYLIST_URL, OUTPUT_FOLDER, SUB_LANG)
