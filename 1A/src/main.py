import os
import json
from pdf_processor import extract_outline # Import your core logic

# Define the input and output directories as specified in the hackathon rules.
INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def process_all_pdfs():
    """
    Iterates through the INPUT_DIR, processes each PDF, and saves
    the resulting JSON outline to the OUTPUT_DIR.
    """
    # Ensure input directory exists (it should, as Docker mounts it)
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found. Ensure it's correctly mounted.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: '{OUTPUT_DIR}'")

    # Iterate over all files in the input directory
    for filename in os.listdir(INPUT_DIR):
        # Process only PDF files (case-insensitive)
        if filename.lower().endswith(".pdf"):
            pdf_full_path = os.path.join(INPUT_DIR, filename)
            # Determine the output JSON filename
            json_filename = os.path.splitext(filename)[0] + ".json"
            json_full_path = os.path.join(OUTPUT_DIR, json_filename)

            print(f"Attempting to process PDF: {filename}")
            try:
                # Call your core extraction function
                outline_data = extract_outline(pdf_full_path)

                # Save the extracted data to a JSON file
                with open(json_full_path, 'w', encoding='utf-8') as f:
                    json.dump(outline_data, f, indent=2, ensure_ascii=False)
                print(f"Successfully generated outline for '{filename}' at '{json_filename}'")

            except Exception as e:
                print(f"Failed to process '{filename}'. Error: {e}")
        else:
            print(f"Skipping non-PDF file: {filename}")

if __name__ == "__main__":
    process_all_pdfs()