import os
import base64
from mistralai import Mistral
from dotenv import load_dotenv


def encode_pdf_to_base64(pdf_path: str) -> str | None:
    """
    Encodes a PDF file to a Base64 string.
    """
    try:
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: The file at {pdf_path} was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while encoding the PDF: {e}")
        return None


def extract_arabic_text_from_pdf(
    pdf_path: str, output_filename: str = "extracted_arabic_text.txt"
):
    """
    Extracts text from a local PDF using Mistral OCR and saves it to a file.
    """
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError(
            "MISTRAL_API_KEY not found. Make sure it is set in your .env file."
        )

    client = Mistral(api_key=api_key)

    print(f"Encoding PDF from path: {pdf_path}")
    base64_pdf = encode_pdf_to_base64(pdf_path)
    if not base64_pdf:
        return

    print("PDF encoded successfully. Sending to Mistral OCR API...")

    try:
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_pdf}",
            },
        )

        # --- CORRECTED RESPONSE HANDLING ---
        # The response object has a 'pages' attribute, which is a list.
        # We need to loop through each page and get its 'markdown' content.
        if ocr_response.pages:
            # Join the markdown content from all pages into a single string
            all_pages_content = [page.markdown for page in ocr_response.pages]
            # Add a separator between pages for better readability
            extracted_text = "\n\n---\n\n".join(all_pages_content)

            print(
                f"\n✅ Successfully extracted content from {len(ocr_response.pages)} page(s)."
            )

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(extracted_text)
            print(f"✅ Extracted text saved to {output_filename}")

            # Optionally print the first 500 characters of the extracted text
            print("\n--- Start of Extracted Text ---")
            print(extracted_text[:500] + "...")

        else:
            print("No content was extracted from the PDF.")

    except Exception as e:
        print(f"An error occurred during the API call or processing: {e}")


# --- Main Execution ---
if __name__ == "__main__":
    load_dotenv()

    pdf_file_path = (
        "/Users/viz1er/Codebase/nasikh-nexus/mistral-ocr/al-arabin-nawawi.pdf"
    )

    extract_arabic_text_from_pdf(pdf_file_path)
