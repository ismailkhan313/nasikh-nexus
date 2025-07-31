import re
import os


def extract_video_ids():
    """
    Reads an HTML source file, extracts 'wvideo' IDs from URLs,
    and writes them to a new text file.
    """
    input_filename = "arabic-202-source-list.txt"
    output_filename = "arabic-202-course-list.txt"

    # --- 1. Check if the input file exists ---
    if not os.path.exists(input_filename):
        print(f"Error: Input file '{input_filename}' not found in this directory.")
        return

    # --- 2. Read the content of the source file ---
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return

    # --- 3. Find all video IDs using regular expressions ---
    # This pattern looks for '?wvideo=' followed by a sequence of letters and numbers.
    # The parentheses ( ... ) capture the ID part.
    pattern = r"\?wvideo=([a-zA-Z0-9]+)"
    found_ids = re.findall(pattern, content)

    # --- 4. Remove duplicate IDs ---
    # Converting the list to a set automatically removes duplicates.
    # Then convert it back to a list.
    unique_ids = list(set(found_ids))

    if not unique_ids:
        print("No video IDs were found in the source file.")
        return

    # --- 5. Write the unique IDs to the output file ---
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            for video_id in unique_ids:
                f.write(video_id + "\n")
    except Exception as e:
        print(f"An error occurred while writing to the output file: {e}")
        return

    print(f"✅ Success! Extracted {len(unique_ids)} unique video IDs.")
    print(f"Results saved to '{output_filename}'.")


if __name__ == "__main__":
    extract_video_ids()
