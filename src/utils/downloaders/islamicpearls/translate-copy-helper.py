import os

# import time
import pyperclip  # Library to copy/paste from the clipboard

# --- Configuration ---
# The folder containing your Arabic Markdown files.
INPUT_DIR = "/Users/viz1er/Codebase/obsidian-vault/05 Projects/Silsila Sacra - Publishing Services/Manuscripts for Publication/Arabic to English Translated Texts/Hikam Ibn Ataillah Sharh Imam Sharnubi/Arabic"
# The folder where the English translations will be saved.
OUTPUT_DIR = "/Users/viz1er/Codebase/obsidian-vault/05 Projects/Silsila Sacra - Publishing Services/Manuscripts for Publication/Arabic to English Translated Texts/Hikam Ibn Ataillah Sharh Imam Sharnubi/English"


def get_translation_from_user(arabic_text: str, original_filename: str) -> str:
    """
    Copies Arabic text to the clipboard and prompts the user to paste the
    English translation back into the terminal.

    Args:
        arabic_text: The full string content of a file to be translated.
        original_filename: The name of the file being processed, for logging.

    Returns:
        The translated English text provided by the user.
    """
    # --- Step 1: Copy the Arabic text to the clipboard ---
    try:
        pyperclip.copy(arabic_text)
        print("-" * 70)
        print(f"File: {original_filename}")
        print("✅ Arabic content has been copied to your clipboard.")
    except pyperclip.PyperclipException as e:
        print(f"[!!] Clipboard error: {e}")
        print(
            "Please manually copy the content from the file and then paste the translation here."
        )

    # --- Step 2: Prompt the user for the translation ---
    print("\n   ACTION REQUIRED:")
    print("   1. Paste the content from your clipboard into the Gemini web UI.")
    print("   2. Copy the English translation it provides.")
    print("   3. Paste the English translation here in the terminal and press Enter.")

    # Use a multi-line input method
    print(
        "\nWaiting for you to paste the English translation (on macOS, press Ctrl+D on a new line when done):"
    )

    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break

    english_translation = "\n".join(lines)
    print("\nReceived translation. Processing next file...")

    return english_translation


def main():
    """
    Main function to run the batch translation process.
    """
    print("Starting semi-automatic batch translation process...")

    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    # Get a list of all .md files to process, sorted numerically
    try:
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.endswith(".md")]
        if not files_to_process:
            print(f"Error: No Markdown files found in the '{INPUT_DIR}' directory.")
            return
        # Sort files based on the number in the filename to process them in order
        files_to_process.sort(key=lambda f: int(f.split()[0]))
    except FileNotFoundError:
        print(
            f"Error: Input directory '{INPUT_DIR}' not found. Please check the folder name and location."
        )
        return
    except (ValueError, IndexError):
        print("Warning: Could not sort files numerically. Processing in default order.")

    print(f"Found {len(files_to_process)} files to translate.")

    # Loop through each file sequentially
    for filename in files_to_process:
        input_filepath = os.path.join(INPUT_DIR, filename)
        output_filename = filename.replace("Arabic", "English")
        output_filepath = os.path.join(OUTPUT_DIR, output_filename)

        # Skip if the English file already exists
        if os.path.exists(output_filepath):
            print(f"Skipping {filename}, English version already exists.")
            continue

        # 1. Read Arabic content
        with open(input_filepath, "r", encoding="utf-8") as f:
            arabic_content = f.read()

        # 2. Get the translation from the user via clipboard
        english_content = get_translation_from_user(arabic_content, filename)

        # 3. Save the new English file
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(english_content)
        print(f"   [SUCCESS] Saved translation to: {output_filename}")

    print("\nBatch translation complete!")


if __name__ == "__main__":
    main()
