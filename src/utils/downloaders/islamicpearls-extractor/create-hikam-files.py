import os
import re


def create_hikam_markdown_files(input_filename="Hikam Arabic 100-264.md"):
    """
    Parses a Markdown file containing numbered aphorisms (Hikam) and their
    commentaries, and saves each complete entry into its own separate
    Markdown file, with the aphorism formatted in bold.

    Args:
        input_filename (str): The name of the input Markdown file.
    """
    # Define the directory where the files will be saved.
    output_dir = "hikam_output"

    # --- 1. Read the source file ---
    try:
        # Open and read the entire content of the source file.
        # UTF-8 encoding is essential for Arabic text.
        with open(input_filename, "r", encoding="utf-8") as f:
            text_block = f.read()
        print(f"Successfully read the input file: {input_filename}")
    except FileNotFoundError:
        print(f"Error: The input file was not found: '{input_filename}'")
        print("Please make sure the file is in the same directory as the script.")
        return  # Exit the function if the file doesn't exist.
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    # --- 2. Setup the output directory ---
    # Create the output directory if it doesn't already exist.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # --- 3. Process the text ---
    # Split the text block into sections. A new section is identified by a line
    # containing only a number, which marks the start of a new aphorism.
    # The regex splits the text before this line, keeping the number with its entry.
    sections = re.split(r"\n(?=\d+\n)", text_block.strip())

    # Loop through each section to process and save it.
    for section in sections:
        # Skip any empty sections that might result from the split.
        if not section.strip():
            continue

        # Split the section into lines to separate the number, aphorism, and commentary.
        # We split a maximum of 2 times to isolate the three parts.
        lines = section.strip().split("\n", 2)

        if len(lines) >= 3:
            # The first line is the number.
            number = lines[0].strip()
            # The second line is the aphorism.
            aphorism = lines[1].strip()
            # The rest of the content is the commentary.
            commentary = lines[2].strip()

            # --- 4. Write one formatted output file per entry ---

            # Construct the filename for the single output file.
            output_filename = os.path.join(output_dir, f"{number} Hikam Arabic.md")

            # Format the content as specified: number, bold aphorism, and commentary.
            markdown_content = f"{number}\n\n**{aphorism}**\n\n{commentary}"

            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                print(f"Successfully created: {output_filename}")
            except IOError as e:
                print(f"Error writing to file {output_filename}: {e}")

        else:
            print(
                f"Warning: Skipping a section that does not have the expected format (number, aphorism, commentary):\n---\n{section}\n---"
            )


# Run the main function when the script is executed.
if __name__ == "__main__":
    create_hikam_markdown_files()
