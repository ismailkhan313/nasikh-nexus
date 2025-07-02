import os
from mistralai import MistralClient

# --- Configuration ---
# It's recommended to set your API key as an environment variable for security
# To do this, in your terminal run: export MISTRAL_API_KEY='your_api_key'
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set.")

client = MistralClient(api_key=api_key)
model = "mistral-ocr-latest"
pdf_path = "arabic_document.pdf"
output_file = "extracted_arabic_text.txt"

# --- OCR Process ---
try:
    with open(pdf_path, "rb") as f:
        # The content of the file is sent as a list of bytes
        pdf_bytes = f.read()

        # Call the Mistral OCR API
        ocr_response = client.ocr.process(
            model=model,
            document={
                "type": "document",
                "document": pdf_bytes,
            },
        )

        # --- Save the Extracted Text ---
        with open(output_file, "w", encoding="utf-8") as out_f:
            for page in ocr_response.pages:
                out_f.write(f"--- Page {page.index + 1} ---\n")
                out_f.write(page.markdown)
                out_f.write("\n\n")

        print(f"Successfully extracted text from '{pdf_path}' to '{output_file}'")

except FileNotFoundError:
    print(f"Error: The file '{pdf_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
