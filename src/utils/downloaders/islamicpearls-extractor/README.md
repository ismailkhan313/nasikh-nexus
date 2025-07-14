# Hikam Parser Script

This Python script is designed to parse a single, large Markdown file containing a collection of the Hikam (aphorisms) and their commentaries. It reads the source file, separates each aphorism, and saves it as an individual, neatly formatted Markdown file.

How It Works
Reads a Source File: The script looks for a file named Hikam Arabic 100-264.md in the same directory where the script is located.

Parses the Content: It intelligently splits the content by identifying the start of each new aphorism, which is expected to be a line containing only the aphorism's number.

Creates Individual Files: For each aphorism found, the script creates a new .md file inside a folder named hikam_output.

File Structure
Input

Source File: Hikam Arabic 100-264.md

Expected Format: Each entry in the source file should be structured as follows:

[Number]
[Aphorism Text]
[Commentary Text]

Output

Output Directory: hikam_output/

Output Files: The script will generate one file per aphorism, named according to its number (e.g., 102 Hikam Arabic.md).

Output Format: Each generated file will contain:

[Number]

**[Aphorism Text]**

[Commentary Text]

How to Use
Place the hikam_parser_script.py file in the same folder as your Hikam Arabic 100-264.md source file.

Run the script from your terminal:

python hikam_parser_script.py

The script will create the hikam_output directory (if it doesn't exist) and populate it with the individual Markdown files.
