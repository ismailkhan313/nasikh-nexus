# flake8: noqa

import os

# List of .txt filenames copied from your input
# Note: I've manually cleaned up the input to be a list of strings.
# In a real-world scenario, you might get these filenames by listing files in a directory.
txt_filenames_input = """
'01 - Authority of the Sunnah and Introduction to Hadith.txt'
'02 - Transmission and Collection of Prophetic Traditions - Ulum Al-Hadith： Ibn Hajar‘s Nukhba [OvLGjniUr38].txt'
'03 - Preservation and Development - Ulum Al-Hadith - Ibn Hajar‘s Nukhba - Shaykh Irshaad Sedick [8ebOuQxpSYE].txt'
'04 - Introduction to Hadith Criticism - Ibn Hajar‘s Nukhba - Shaykh Irshaad Sedick [YFpAcYxHq7w].txt'
'05 – Emergence of Fabrication - Ulum Al-Hadith - Ibn Hajar‘s Nukhba - Shaykh Irshaad Sedick [Cw3DmuMZOkQ].txt'
"06 - Hadith Terminology - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [FuDvEnV0otk].txt"
'07 – Mutawatir and Ahad - Ulum Al-Hadith - Ibn Hajar‘s Nukhba - Shaykh Irshaad Sedick [hMhqKdTZmNQ].txt'
"08 - Sahih - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [KMseG367C1g].txt"
"09 - Hasan - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [iMRdHjmkYZ4].txt"
"10 - Comparing Chains - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [IIquAUfxQMI].txt"
"11 - Reasons for Rejection - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [rRMs8bnQmGI].txt"
"12 - Reasons for Rejection - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick - [CKnvkuTLbq0].txt"
"13 - Reasons for Rejection - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [h5U7qZe4oKo].txt"
"14 - Reasons for Rejection - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [b10R7NKHJKk].txt"
"15 - Isnad Attribution - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [IIxNk_iAW18].txt"
"16 - Forms of Conveyence - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [6YmQtOfUnGo].txt"
"17 - Names of Narrators and Conclusion - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [68-uYnLD03A].txt"
"18 - Orientalism, Modernity and Hadith - Ibn Hajar's Nukhba - Shaykh Irshaad Sedick [7kLveK8XSLU].txt"
"""

# Clean up the input and extract just the filenames
# This handles lines that might be empty or just whitespace,
# and removes the leading/trailing quotes.
raw_filenames = [line.strip() for line in txt_filenames_input.strip().split('\n')]
txt_filenames = [name.strip("'\"") for name in raw_filenames if name.endswith(".txt'\"")]


# --- If you want to get filenames directly from a directory ---
# --- UNCOMMENT THE FOLLOWING SECTION and comment out the above `txt_filenames_input` and processing ---
# import glob
#
# # Get all .txt files in the current directory
# txt_filenames = glob.glob("*.txt")
#
# # If your files are in a specific directory, change "*.txt" to "your_directory_path/*.txt"
# # For example: txt_filenames = glob.glob("my_text_files/*.txt")
# # --- END OF DIRECTORY LISTING SECTION ---


if not txt_filenames:
    print("No .txt files found from the input.")
else:
    print(f"Found {len(txt_filenames)} .txt files to process.\n")

    for txt_filename in txt_filenames:
        # Create the base name by removing the '.txt' extension
        base_name, _ = os.path.splitext(txt_filename)
        md_filename = base_name + ".md"

        try:
            # Create the new .md file.
            # 'w' mode will create the file if it doesn't exist,
            # and overwrite it if it does.
            # If you want to avoid overwriting, check if the file exists first:
            # if not os.path.exists(md_filename):
            #     with open(md_filename, 'w') as md_file:
            #         pass # Creates an empty file
            #     print(f"Created: {md_filename}")
            # else:
            #     print(f"Skipped (already exists): {md_filename}")

            with open(md_filename, 'w') as md_file:
                # You can optionally write some initial content here, e.g., the title
                # md_file.write(f"# {base_name}\n")
                pass # Creates an empty file

            print(f"Successfully created: {md_filename}")

        except OSError as e:
            print(f"Error creating file {md_filename}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with {txt_filename}: {e}")

    print("\nScript finished.")