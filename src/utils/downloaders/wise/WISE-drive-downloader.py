import os
import requests
import re
import sys

# --- Configuration ---
# Finds the 'wise' folder where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "links.txt")
DOWNLOAD_FOLDER = os.path.expanduser("~/Downloads")


def get_confirm_token(response):
    """Extracts the Google Drive 'download anyway' token from cookies."""
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def download_video():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: links.txt not found in {BASE_DIR}")
        return

    with open(INPUT_FILE, "r") as f:
        links = [line.strip() for line in f if "id=" in line]

    if not links:
        print("No valid Google Drive links found.")
        return

    # Use a Session to persist cookies (the "bypass" token)
    session = requests.Session()

    print(f"Found {len(links)} videos. Starting high-speed download...\n")

    for i, url in enumerate(links, 1):
        try:
            # 1. Extract the unique File ID
            file_id_match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
            if not file_id_match:
                print(f"Skipping link {i}: Could not find File ID.")
                continue
            file_id = file_id_match.group(1)

            # 2. Ping Google to get the confirmation token (bypass virus scan page)
            confirm_url = "https://drive.google.com/uc?export=download"
            response = session.get(confirm_url, params={"id": file_id}, stream=True)
            token = get_confirm_token(response)

            if token:
                # If file is large, we must re-request with the token
                params = {"id": file_id, "confirm": token}
                response = session.get(confirm_url, params=params, stream=True)

            # 3. Handle File Naming
            # We force the .mp4 extension since we know these are videos
            content_disposition = response.headers.get("content-disposition")
            if content_disposition:
                found_name = re.findall('filename="?([^";]+)"?', content_disposition)
                filename = found_name[0] if found_name else f"video_{file_id}.mp4"
            else:
                filename = f"video_{file_id}.mp4"

            # Ensure it ends in .mp4
            if not filename.lower().endswith(".mp4"):
                filename = os.path.splitext(filename)[0] + ".mp4"

            save_path = os.path.join(DOWNLOAD_FOLDER, filename)

            print(f"[{i}/{len(links)}] Downloading: {filename}")

            # 4. Stream the data to the Downloads folder
            with open(save_path, "wb") as f:
                downloaded = 0
                # Using 1MB chunks for speed and stability
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        sys.stdout.write(
                            f"\r    Progress: {downloaded // (1024*1024)} MB saved..."
                        )
                        sys.stdout.flush()

            print(f"\n    Done: {filename}\n")

        except Exception as e:
            print(f"\n    Error with link {i}: {e}\n")

    print("=" * 40)
    print("FINISHED: All videos are now in your Downloads folder.")
    print("=" * 40)

    # macOS Speech Alert
    os.system('say "Your video downloads are finished"')


if __name__ == "__main__":
    download_video()
