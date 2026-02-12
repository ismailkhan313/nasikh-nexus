import os
from pathlib import Path
from collections import defaultdict


def combine_logic_files():
    # 1. Ask the user for the folder path
    path_input = input(
        "Please enter the full path to the folder containing your files: "
    ).strip()

    # Clean up quotes if the user copied/pasted the path (common on Windows/Mac)
    path_input = path_input.replace('"', "").replace("'", "")

    source_dir = Path(path_input)

    # Validate if the path exists
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"Error: The path '{source_dir}' does not exist or is not a folder.")
        return

    # 2. Create the output directory inside the source directory
    output_dir = source_dir / "Concatenated_Lessons"
    output_dir.mkdir(exist_ok=True)

    # 3. Group files by their major lesson number (e.g., "1" from "1.1 Logic.txt")
    groups = defaultdict(list)

    print("Scanning for files...")
    for file in source_dir.glob("*.txt"):
        # filenames like '1.1 Logic.txt'
        filename = file.name
        if "." in filename:
            try:
                # Get the part before the first dot
                major_lesson_str = filename.split(".")[0]
                if major_lesson_str.isdigit():
                    groups[int(major_lesson_str)].append(file)
            except (ValueError, IndexError):
                continue

    if not groups:
        print(
            "No matching lesson files (e.g., '1.1 Logic.txt') were found in that folder."
        )
        return

    # 4. Process each group
    for lesson_num in sorted(groups.keys()):
        # Sort sub-lessons (1.1, 1.2, 1.10) naturally
        files_to_combine = sorted(
            groups[lesson_num],
            key=lambda f: [
                int(part) if part.isdigit() else part
                for part in f.name.replace(" ", ".").split(".")
            ],
        )

        output_filename = f"Lesson_{lesson_num}_Complete.txt"
        output_path = output_dir / output_filename

        print(f"Creating {output_filename}...")

        with open(output_path, "w", encoding="utf-8") as outfile:
            for file_path in files_to_combine:
                with open(file_path, "r", encoding="utf-8") as infile:
                    # Optional: Separator for clarity
                    outfile.write(f"\n--- {file_path.name} ---\n\n")
                    outfile.write(infile.read())
                    outfile.write("\n\n")  # Double newline between sub-lessons

    print(f"\nSuccess! 15 lessons created in: {output_dir}")


if __name__ == "__main__":
    combine_logic_files()
