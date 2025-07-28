import pdfplumber
import PyPDF2
import re
from typing import Dict, List, Tuple
from heading_detector import HeadingDetector

class PDFProcessor:
    def __init__(self):
        self.heading_detector = HeadingDetector()
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """Extract title and outline from PDF"""
        try:
            # Try to extract title from metadata first
            title = self._extract_title_from_metadata(pdf_path)
            
            # Extract text with formatting information
            pages_data = self._extract_pages_with_formatting(pdf_path)
            
            # If no title from metadata, try to extract from first page
            if not title:
                title = self._extract_title_from_content(pages_data)
            
            # Detect headings
            outline = self.heading_detector.detect_headings(pages_data)
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            print(f"Error in extract_outline: {str(e)}")
            return {"title": "", "outline": []}
    
    def _extract_title_from_metadata(self, pdf_path: str) -> str:
        """Extract title from PDF metadata"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                if pdf_reader.metadata and pdf_reader.metadata.title:
                    return pdf_reader.metadata.title.strip()
        except:
            pass
        return ""
    
    def _extract_title_from_content(self, pages_data: List) -> str:
        """Extract title from first page content"""
        if not pages_data:
            return ""
        
        first_page = pages_data[0]
        
        # Look for the largest font size text on first page
        max_font_size = 0
        title_candidates = []
        
        for char_data in first_page['chars']:
            if char_data['size'] > max_font_size:
                max_font_size = char_data['size']
                title_candidates = [char_data['text']]
            elif char_data['size'] == max_font_size:
                title_candidates.append(char_data['text'])
        
        # Combine title candidates
        if title_candidates:
            title = ''.join(title_candidates).strip()
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            # Take first reasonable length title
            sentences = re.split(r'[.!?]\s+', title)
            if sentences:
                return sentences[0][:100]  # Limit title length
        
        return ""
    
    def _extract_pages_with_formatting(self, pdf_path: str) -> List[Dict]:
        """Extract pages with character-level formatting information"""
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    chars = page.chars
                    
                    # Group characters into lines
                    lines = self._group_chars_into_lines(chars)
                    
                    pages_data.append({
                        'page_num': page_num,
                        'chars': chars,
                        'lines': lines
                    })
                    
        except Exception as e:
            print(f"Error extracting pages: {str(e)}")
        
        return pages_data
    
    def _group_chars_into_lines(self, chars: List) -> List[Dict]:
        """Group characters into lines based on y-coordinate"""
        if not chars:
            return []
        
        lines = []
        current_line = []
        current_y = None
        y_tolerance = 2  # Tolerance for same line
        
        # Sort chars by y-coordinate (top to bottom) then x-coordinate (left to right)
        sorted_chars = sorted(chars, key=lambda c: (-c['y0'], c['x0']))
        
        for char in sorted_chars:
            if current_y is None or abs(char['y0'] - current_y) > y_tolerance:
                # Start new line
                if current_line:
                    lines.append(self._process_line(current_line))
                current_line = [char]
                current_y = char['y0']
            else:
                # Add to current line
                current_line.append(char)
        
        # Add last line
        if current_line:
            lines.append(self._process_line(current_line))
        
        return lines
    
    def _process_line(self, chars: List) -> Dict:
        """Process a line of characters"""
        if not chars:
            return {'text': '', 'font_size': 0, 'is_bold': False}
        
        # Sort by x-coordinate
        chars = sorted(chars, key=lambda c: c['x0'])
        
        # Extract text
        text = ''.join(char['text'] for char in chars).strip()
        
        # Get dominant font properties
        font_sizes = [char['size'] for char in chars if char['text'].strip()]
        font_size = max(font_sizes) if font_sizes else 0
        
        # Check if bold (simplified check based on font name)
        is_bold = any('bold' in str(char.get('fontname', '')).lower() 
                     for char in chars if char['text'].strip())
        
        return {
            'text': text,
            'font_size': font_size,
            'is_bold': is_bold,
            'y_position': chars[0]['y0'] if chars else 0
        }