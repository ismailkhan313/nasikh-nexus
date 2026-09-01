import re
import os

# --- MANUALLY CHANGE THIS VARIABLE AS NEEDED ---
BASE_URL = "https://online.wise.edu.jo/english/pluginfile.php/4416/mod_scorm/content/1"
# -----------------------------------------------


def extract_video_urls():
    file_path = "data.js"

    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found in the current directory.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex explanation:
        # Looks for the literal string "story_content/video_"
        # followed by any alphanumeric characters or underscores
        # ending with ".mp4"
        pattern = r"story_content/video_[a-zA-Z0-9_]+\.mp4"

        # Find all matches
        matches = re.findall(pattern, content)

        # Convert to a set to get unique URLs, then sort them
        unique_videos = sorted(list(set(matches)))

        if not unique_videos:
            print("No video URLs found in data.js.")
            return

        print(f"--- Found {len(unique_videos)} Unique Videos ---")
        for video in unique_videos:
            # Clean up potential double slashes if BASE_URL ends with one
            base = BASE_URL.rstrip("/")
            full_link = f"{base}/{video}"
            print(full_link)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    extract_video_urls()
