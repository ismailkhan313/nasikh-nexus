import fitz  # PyMuPDF
import os
import re
import operator


def get_font_styles(doc):
    """
    Extracts font styles (size and count) from the document to identify headings.
    """
    styles = {}
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b["type"] == 0:  # Text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        size = round(s["size"])
                        styles[size] = styles.get(size, 0) + 1

    # Sort styles by frequency
    sorted_styles = sorted(styles.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_styles


def identify_chapter_headings(doc, heading_font_size):
    """
    Identifies chapter headings based on font size and keywords.
    """
    chapters = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b["type"] == 0:  # Text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        if round(s["size"]) == heading_font_size:
                            # Use regex to find common chapter keywords
                            if re.search(
                                r"(الفصل|باب|الجزء)", s["text"], re.IGNORECASE
                            ):
                                chapters.append((page_num, s["text"].strip()))
    return chapters


def pdf_to_markdown_chapters(pdf_path):
    """
    Splits a PDF into Markdown files, one for each chapter.
    """
    # Create a directory to store the markdown files
    output_dir = os.path.splitext(pdf_path)[0] + "_chapters"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    doc = fitz.open(pdf_path)

    # Try to get chapters from the table of contents first
    toc = doc.get_toc()
    chapters = []
    if toc:
        print("Found Table of Contents. Using it to split chapters.")
        for item in toc:
            level, title, page = item
            # Assuming top-level entries are chapters
            if level == 1:
                chapters.append((page - 1, title))  # page is 1-based
    else:
        print("No Table of Contents found. Analyzing font styles to identify chapters.")
        styles = get_font_styles(doc)
        if not styles:
            print("Could not determine font styles. Exiting.")
            return

        # Assuming the most common font size is the body text and the next largest is a heading
        # This might need adjustment based on the document's structure
        body_font_size = styles[0][0]
        heading_font_size = 0
        for size, count in styles:
            if size > body_font_size:
                heading_font_size = size
                break

        if heading_font_size == 0:
            print("Could not identify a clear heading font size. Exiting.")
            return

        print(
            f"Identified body font size: {body_font_size}, and heading font size: {heading_font_size}"
        )
        chapters = identify_chapter_headings(doc, heading_font_size)

    if not chapters:
        print("No chapters found. The script will not generate any files.")
        return

    # Process each chapter
    for i, (start_page, title) in enumerate(chapters):
        # Determine the end page for the current chapter
        if i + 1 < len(chapters):
            end_page = chapters[i + 1][0]
        else:
            end_page = len(doc)

        # Extract the text for the current chapter
        chapter_text = ""
        for page_num in range(start_page, end_page):
            chapter_text += doc[page_num].get_text()

        # Sanitize the title to create a valid filename
        filename = re.sub(r'[\\/*?:"<>|]', "", title)
        filename = f"{i+1:02d}_{filename}.md"
        filepath = os.path.join(output_dir, filename)

        # Write the chapter text to a markdown file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(chapter_text)

        print(f"Created chapter: {filepath}")

    print("\nProcessing complete.")
    print(f"Markdown files have been saved in: {output_dir}")


if __name__ == "__main__":
    # To run this script, replace 'your_document.pdf' with the path to your PDF file.
    # For example:
    # pdf_to_markdown_chapters("my_arabic_book.pdf")

    # Please provide the path to your PDF file here
    pdf_path = "/Users/viz1er/Ismail's Library/Ahmad ibn Muhammad ibn `Ayyad al-Shafi`i/PDF Al-Mafakhir al-Aliyyah fi al-Ma'athir al-Shadhiliyyah (Arabic_ almfakhr al`ly@ fy almathr a (6500)/PDF Al-Mafakhir al-Aliyyah fi al-Ma'athir - Ahmad ibn Muhammad ibn `Ayyad al-Shafi`i.pdf"

    if pdf_path == "your_document.pdf":
        print(
            "Please update the 'pdf_path' variable in the script with the path to your PDF file."
        )
    elif not os.path.exists(pdf_path):
        print(f"Error: The file '{pdf_path}' was not found.")
    else:
        pdf_to_markdown_chapters(pdf_path)
