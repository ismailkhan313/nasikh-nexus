import requests
import os
import json
import getpass  # Used to securely prompt for the password
import time  # Used for adding delays between retries
from bs4 import BeautifulSoup  # Used to parse HTML and find the login token

# --- CONFIGURATION ---
# Set the path where the downloaded videos will be saved.
OUTPUT_DIRECTORY = "/Users/viz1er/Documents/audio-lectures/WISE UNIVERSITY HANAFI FIQH BA /intro-to-hanafi-fiqh"


# --- MOODLE LOGIN CREDENTIALS ---
# You must update these values for your specific Moodle portal.
LOGIN_URL = "https://online.wise.edu.jo/english/login/index.php"  # The full URL of the login page
USERNAME = "3241790946"  # Replace with your Moodle username
# ---------------------


def load_lectures_from_file(filepath):
    """
    Loads lecture URLs from a JSON file.

    Args:
        filepath (str): The absolute path to the file to load the lecture data from.

    Returns:
        dict: A dictionary containing the lecture data, or None if an error occurs.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' is not a valid JSON file.")
        return None


def login_to_moodle(session):
    """
    Logs into Moodle by first fetching a security token from the login page.

    Args:
        session: A requests.Session object.

    Returns:
        True if login is successful, False otherwise.
    """
    try:
        # 1. First, visit the login page to get the session cookie and the login token.
        print("Fetching login page to get security token...")
        login_page_response = session.get(LOGIN_URL, timeout=30)
        login_page_response.raise_for_status()

        # 2. Parse the HTML to find the 'logintoken'. Moodle uses this for security.
        soup = BeautifulSoup(login_page_response.text, "lxml")
        logintoken_input = soup.find("input", {"name": "logintoken"})

        if not logintoken_input:
            print("Error: Could not find the 'logintoken' on the page.")
            print(
                "The website's login form may have changed. The script needs to be updated."
            )
            return False

        logintoken = logintoken_input["value"]
        print("Security token found.")

        # 3. Prompt for password and build the complete login payload.
        password = getpass.getpass("Enter your Moodle password: ")
        login_payload = {
            "username": USERNAME,
            "password": password,
            "logintoken": logintoken,
        }

        # 4. Send the POST request with the credentials and the token.
        print(f"Attempting to log in as '{USERNAME}'...")
        response = session.post(LOGIN_URL, data=login_payload, timeout=30)
        response.raise_for_status()

        # 5. Check if the login was successful.
        # A successful login should redirect away from the login page.
        if "login/index.php" in response.url or "Invalid login" in response.text:
            print("Login failed. Please double-check your username and password.")
            return False

        print("Login successful!")
        return True

    except requests.exceptions.RequestException as e:
        print(f"A network error occurred during login: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during the login process: {e}")
        return False


def download_videos():
    """
    Logs into Moodle and downloads videos, saving them to the specified directory.
    Implements a retry mechanism for failed downloads.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lecture_file_path = os.path.join(script_dir, "wise-uni.txt")

    lectures = load_lectures_from_file(lecture_file_path)
    if not lectures:
        return

    # Create a session object to persist cookies across requests
    with requests.Session() as session:
        # Attempt to log in first
        if not login_to_moodle(session):
            return  # Exit if login fails

        # If login is successful, proceed to download videos
        output_dir = OUTPUT_DIRECTORY
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")

        for lecture_num_str, video_urls in lectures.items():
            lecture_num = int(lecture_num_str)
            print(f"\n--- Starting Lecture {lecture_num} ---")

            for i, url in enumerate(video_urls):
                part_num = i + 1
                filename = f"{lecture_num:02d}-{part_num}.mp4"
                filepath = os.path.join(output_dir, filename)

                # Check if the file already exists to avoid re-downloading
                if os.path.exists(filepath):
                    print(f"Skipping {filename}, already exists.")
                    continue

                # --- Retry Logic ---
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        print(
                            f"Downloading: {filename} (Attempt {attempt + 1}/{max_retries})"
                        )
                        # Use the logged-in session to download the file with a longer timeout
                        response = session.get(url, stream=True, timeout=90)
                        response.raise_for_status()  # Will raise an error for bad status codes

                        with open(filepath, "wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"Successfully downloaded {filename}")
                        break  # Exit the retry loop on success

                    except requests.exceptions.RequestException as e:
                        print(f"An error occurred while downloading {filename}: {e}")
                        if attempt < max_retries - 1:
                            # Wait before retrying, increasing the wait time with each attempt
                            wait_time = (attempt + 1) * 5  # e.g., 5s, 10s
                            print(f"Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                        else:
                            print(
                                f"Failed to download {filename} after {max_retries} attempts."
                            )
                # --- End Retry Logic ---

    print("\nAll video downloads completed.")


if __name__ == "__main__":
    # To run this script, you need to install 'requests' and 'beautifulsoup4'.
    # You can install them by running this command in your terminal:
    # pip install requests beautifulsoup4 lxml

    # Before running, make sure to set your USERNAME at the top of the script.
    if USERNAME == "your_moodle_username":
        print("Please update the 'USERNAME' variable in the script before running.")
    else:
        download_videos()
