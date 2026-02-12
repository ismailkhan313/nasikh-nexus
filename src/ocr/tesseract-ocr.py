import pytesseract
from pdf2image import convert_from_path
import pypdf
import io

# from PIL import Image  # Import the full Image module from Pillow


def preprocess_image(image):
    """Converts a PIL image to high-contrast black and white for better OCR."""
    # Convert to grayscale first
    processed = image.convert("L")
    # Apply a threshold to make it pure black and white
    processed = processed.point(lambda x: 0 if x < 180 else 255, "1")
    return processed


def create_searchable_pdf(pdf_path, output_path):
    """
    Performs OCR on an image-based PDF and saves it as a new, searchable PDF.
    """
    pdf_writer = pypdf.PdfWriter()

    try:
        print("➡️ Starting PDF conversion to images...")
        images = convert_from_path(
            pdf_path,
            300,
            # You can remove the page limits to run on the whole document
            # first_page=1,
            # last_page=20
        )
        print(f"✅ PDF converted to {len(images)} images.")

        for i, image in enumerate(images):
            print(f"⚙️  Processing page {i + 1}/{len(images)}...")

            # --- NEW STEP: PRE-PROCESS THE IMAGE ---
            print("    - Pre-processing image for clarity...")
            processed_image = preprocess_image(image)

            # Pass the CLEANED image to Tesseract
            page_as_pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                processed_image,  # Use the processed image here
                lang="eng+ara",
                extension="pdf",
            )

            page_pdf_reader = io.BytesIO(page_as_pdf_bytes)
            reader = pypdf.PdfReader(page_pdf_reader)
            pdf_writer.add_page(reader.pages[0])

        with open(output_path, "wb") as f:
            pdf_writer.write(f)

        print(f"\n🎉 Success! Searchable PDF saved to: {output_path}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")


# --- USAGE ---
input_pdf_path = "/Users/viz1er/Ismail's Library/Ibn Ajurum/A Commentary on al-Ajrumiyyah (Al-Tuhfat as-Saniyyah bi Sharh al-Muqaddimat al-Ajurumiyyah) (3408)/A Commentary on al-Ajrumiyyah (Al-Tuhfat a - Ibn Ajurum.pdf"
output_path = "/Users/viz1er/Ismail's Library/Ibn Ajurum/A Commentary on al-Ajrumiyyah (Al-Tuhfat as-Saniyyah bi Sharh al-Muqaddimat al-Ajurumiyyah) (3408)/test_processed.pdf"

create_searchable_pdf(input_pdf_path, output_path)
