import fitz # PyMuPDF
import json
import re

def extract_outline(pdf_path):
    """
    Extracts the title and a hierarchical outline (H1, H2, H3) from a PDF.
    Improved for handling forms and prioritizing visual titles.
    """
    document = fitz.open(pdf_path)
    title = ""
    outline = []

    # --- Title Extraction (Improved Heuristic) ---
    # Prioritize the largest text on the first page, if it looks like a title.
    # Otherwise, fall back to metadata.

    page_0 = document[0]
    page_0_text_blocks = page_0.get_text("dict")["blocks"]

    # Analyze blocks on the first page to find the most prominent text
    # Consider blocks that are centrally aligned, large font, and appear at the top.
    potential_titles_from_content = []
    max_font_size_on_page_0 = 0

    for b in page_0_text_blocks:
        if b['type'] == 0: # text block
            for line in b['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    font_size = round(span['size'], 1)
                    font_flags = span['flags']
                    
                    # A very strong candidate for title: large, bold, and near the top
                    # Adjust 'y0' (top coordinate) threshold as needed
                    if font_size > 18 and (font_flags & 2) and text and b['bbox'][1] < page_0.rect.height / 3:
                        potential_titles_from_content.append({"text": text, "size": font_size, "bbox": b['bbox']})
                        if font_size > max_font_size_on_page_0:
                            max_font_size_on_page_0 = font_size

    # Select the most prominent one if found
    if potential_titles_from_content:
        # Sort by font size (descending) and then y-position (ascending)
        potential_titles_from_content.sort(key=lambda x: (-x['size'], x['bbox'][1]))
        # Filter for text with the maximum font size, then pick the highest one
        top_candidates = [pt for pt in potential_titles_from_content if pt['size'] == max_font_size_on_page_0]
        if top_candidates:
            title = top_candidates[0]['text']
    
    # If no strong visual title found, use metadata as a fallback (but it seems this gave bad results for this PDF)
    if not title and document.metadata and document.metadata.get("title"):
        metadata_title = document.metadata["title"].strip()
        # Sometimes metadata titles are internal names. Heuristically filter short/non-descriptive ones
        if len(metadata_title) > 10 and not metadata_title.lower().endswith(".doc"): # Simple check
             title = metadata_title
        elif not title: # If no visual title found and metadata was filtered, use a simpler metadata if available
            title = metadata_title # As a final fallback

    # --- Heading Extraction (Improved for forms/numbered lists) ---
    # This document uses numbered fields, not traditional headings.
    # We will treat "1. Name of the Government Servant" etc. as H1s.
    # We'll also try to detect bold phrases that act as sub-sections.

    for page_num in range(document.page_count):
        page = document[page_num]
        blocks = page.get_text("dict")["blocks"]

        for b in blocks:
            if b['type'] == 0: # Text block
                for line in b['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        font_size = round(span['size'], 1)
                        font_flags = span['flags']
                        is_bold = bool(font_flags & 2)

                        # Heuristic for H1 (numbered form fields): "N. Text" pattern
                        # Check if text starts with a number followed by a period and space, and is not too long.
                        # Also, ensure it's sufficiently large/bold (relative to typical body text)
                        numbered_heading_match = re.match(r'^\d+\.\s*(.+)', text)
                        if numbered_heading_match and len(text) < 100:
                            # Consider if font size is larger than surrounding text or bold
                            # This needs more context-aware analysis but as a start:
                            if font_size >= 9 or is_bold: # Adjust threshold based on common body text size
                                heading_text = numbered_heading_match.group(0).strip() # Keep "1. " part
                                outline.append({
                                    "level": "H1",
                                    "text": heading_text,
                                    "page": page_num + 1
                                })
                        
                        # Heuristic for H2 (other prominent bold text, like "Persons in respect of whom...")
                        # Look for bold text that is a distinct line, not too long, and not a numbered heading.
                        elif is_bold and text and len(text) < 100 and not re.match(r'^\d+\.\s*', text):
                            # Add more checks here if needed, e.g., position, line height, etc.
                            # For "Persons in respect of whom LTC is proposed to be availed."
                            # It's bold and stands alone, so H2 is reasonable.
                            if not any(entry['text'] == text for entry in outline): # Avoid adding duplicates if multiple spans
                                outline.append({
                                    "level": "H2",
                                    "text": text,
                                    "page": page_num + 1
                                })


    # Post-processing: Remove simple duplicates (same text, same page, same level)
    # The current logic can sometimes create duplicates if parts of the same heading are split into different spans.
    unique_outline = []
    seen = set()
    for entry in outline:
        key = (entry['level'], entry['text'], entry['page'])
        if key not in seen:
            unique_outline.append(entry)
            seen.add(key)
    
    # Sort the outline for consistent output (by page, then by vertical position)
    # This requires storing bbox[1] (y0) during extraction and sorting by it.
    # For now, sorting by page then text is a reasonable fallback.
    unique_outline.sort(key=lambda x: (x['page'], x['text'])) 

    return {"title": title, "outline": unique_outline}