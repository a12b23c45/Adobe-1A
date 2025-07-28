import re
from typing import List, Dict, Tuple
from collections import Counter

class HeadingDetector:
    def __init__(self):
        # Common heading patterns
        self.heading_patterns = [
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
            r'^\d+\.\d+\.?\s+[A-Z]',  # "1.1. Subsection" or "1.1 Subsection"
            r'^\d+\.\d+\.\d+\.?\s+[A-Z]',  # "1.1.1. Sub-subsection"
            r'^[A-Z][A-Z\s]+$',  # "INTRODUCTION" (all caps)
            r'^Chapter\s+\d+',  # "Chapter 1"
            r'^Section\s+\d+',  # "Section 1"
            r'^\w+\s+\d+',  # Generic "Word Number" pattern
        ]
    
    def detect_headings(self, pages_data: List[Dict]) -> List[Dict]:
        """Detect headings across all pages"""
        all_lines = []
        
        # Collect all lines with page numbers
        for page in pages_data:
            for line in page['lines']:
                if line['text'].strip():
                    all_lines.append({
                        **line,
                        'page': page['page_num']
                    })
        
        # Analyze font sizes
        font_analysis = self._analyze_font_sizes(all_lines)
        
        # Detect headings
        headings = []
        
        for line in all_lines:
            heading_level = self._classify_heading(line, font_analysis)
            if heading_level:
                headings.append({
                    'level': heading_level,
                    'text': line['text'].strip(),
                    'page': line['page']
                })
        
        # Post-process and clean headings
        headings = self._post_process_headings(headings)
        
        return headings
    
    def _analyze_font_sizes(self, lines: List[Dict]) -> Dict:
        """Analyze font size distribution to identify heading thresholds"""
        font_sizes = [line['font_size'] for line in lines if line['font_size'] > 0]
        
        if not font_sizes:
            return {'body_size': 12, 'h3_threshold': 13, 'h2_threshold': 15, 'h1_threshold': 18}
        
        font_counter = Counter(font_sizes)
        
        # Most common font size is likely body text
        body_size = font_counter.most_common(1)[0][0]
        
        # Set thresholds based on body size
        h3_threshold = body_size + 1
        h2_threshold = body_size + 3
        h1_threshold = body_size + 6
        
        return {
            'body_size': body_size,
            'h3_threshold': h3_threshold,
            'h2_threshold': h2_threshold,
            'h1_threshold': h1_threshold
        }
    
    def _classify_heading(self, line: Dict, font_analysis: Dict) -> str:
        """Classify if a line is a heading and determine its level"""
        text = line['text'].strip()
        font_size = line['font_size']
        is_bold = line['is_bold']
        
        # Skip very short or very long text
        if len(text) < 2 or len(text) > 200:
            return None
        
        # Skip common non-heading patterns
        if self._is_likely_not_heading(text):
            return None
        
        # Check if matches heading patterns
        pattern_match = self._matches_heading_pattern(text)
        
        # Font size based classification
        size_based_level = None
        if font_size >= font_analysis['h1_threshold']:
            size_based_level = 'H1'
        elif font_size >= font_analysis['h2_threshold']:
            size_based_level = 'H2'
        elif font_size >= font_analysis['h3_threshold']:
            size_based_level = 'H3'
        
        # Determine final classification
        if pattern_match:
            # If matches numbered pattern, determine level from numbering
            if re.match(r'^\d+\.\d+\.\d+', text):
                return 'H3'
            elif re.match(r'^\d+\.\d+', text):
                return 'H2'
            elif re.match(r'^\d+\.?', text):
                return 'H1'
            else:
                return size_based_level or 'H2'
        
        # If bold and larger than body text
        if is_bold and font_size > font_analysis['body_size']:
            return size_based_level or 'H3'
        
        # If significantly larger than body text
        if size_based_level:
            return size_based_level
        
        return None
    
    def _matches_heading_pattern(self, text: str) -> bool:
        """Check if text matches common heading patterns"""
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_likely_not_heading(self, text: str) -> bool:
        """Check if text is likely not a heading"""
        # Skip page numbers, dates, URLs, etc.
        skip_patterns = [
            r'^\d+$',  # Just numbers
            r'^\d{1,2}/\d{1,2}/\d{2,4}$',  # Dates
            r'https?://',  # URLs
            r'^\d+\s*$',  # Page numbers
            r'^Page\s+\d+',  # "Page X"
            r'^\w+@\w+\.',  # Email addresses
            r'^\$\d+',  # Prices
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # Skip if mostly punctuation
        if len(re.sub(r'[^\w\s]', '', text)) < len(text) * 0.5:
            return True
        
        return False
    
    def _post_process_headings(self, headings: List[Dict]) -> List[Dict]:
        """Post-process headings to remove duplicates and clean up"""
        # Remove duplicates (same text on same page)
        seen = set()
        cleaned_headings = []
        
        for heading in headings:
            key = (heading['text'].lower(), heading['page'])
            if key not in seen:
                seen.add(key)
                cleaned_headings.append(heading)
        
        # Sort by page number
        cleaned_headings.sort(key=lambda x: x['page'])
        
        return cleaned_headings