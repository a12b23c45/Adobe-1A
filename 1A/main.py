#!/usr/bin/env python3
import os
import json
import glob
from pdf_processor import PDFProcessor

def main():
    input_dir = "/app/input"
    output_dir = "/app/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Process all PDF files in input directory
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    for pdf_path in pdf_files:
        try:
            # Extract filename without extension
            filename = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = os.path.join(output_dir, f"{filename}.json")
            
            print(f"Processing: {pdf_path}")
            
            # Extract outline
            result = processor.extract_outline(pdf_path)
            
            # Save to JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Saved: {output_path}")
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            # Create empty result for failed processing
            error_result = {"title": "", "outline": []}
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2)

if __name__ == "__main__":
    main()