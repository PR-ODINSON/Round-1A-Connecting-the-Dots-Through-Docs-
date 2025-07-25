#!/usr/bin/env python3
"""
Heading Classifier Module
Uses font size, style, and position heuristics to classify text as H1, H2, or H3 headings
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

class HeadingClassifier:
    """Classify text as headings using layout and font heuristics"""
    
    def __init__(self):
        """Initialize the heading classifier"""
        self.heading_patterns = [
            # Chapter/Section patterns
            r'^(chapter|section|part)\s+\d+',
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
            r'^\d+\.\d+\.?\s+[A-Z]',  # "1.1 Overview" or "1.1. Overview"
            r'^\d+\.\d+\.\d+\.?\s+[A-Z]',  # "1.1.1 Details"
            
            # Common heading words
            r'^(introduction|conclusion|summary|overview|background|methodology|results|discussion|references)',
            r'^(abstract|acknowledgments|appendix|bibliography|glossary)',
            
            # All caps (potential headings)
            r'^[A-Z\s]{3,}$',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.heading_patterns]
        
        # Minimum and maximum reasonable heading lengths
        self.min_heading_length = 3
        self.max_heading_length = 200
    
    def classify_headings(self, pages_data: List[Dict], font_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Classify text blocks as headings based on font and layout heuristics
        
        Args:
            pages_data: List of page data from PDF parser
            font_metrics: Font usage statistics
            
        Returns:
            List of classified headings with type, text, and page number
        """
        headings = []
        
        # Calculate font size thresholds
        size_thresholds = self._calculate_font_thresholds(font_metrics)
        logger.info(f"📏 Font size thresholds: {size_thresholds}")
        
        for page_data in pages_data:
            page_headings = self._classify_page_headings(
                page_data, 
                font_metrics, 
                size_thresholds
            )
            headings.extend(page_headings)
        
        # Post-process headings to ensure hierarchy makes sense
        headings = self._refine_heading_hierarchy(headings)
        
        logger.info(f"🏷️  Classified {len(headings)} headings")
        return headings
    
    def extract_title(self, pages_data: List[Dict], font_metrics: Dict[str, Any], filename: str) -> str:
        """
        Extract document title from the first page or use filename as fallback
        
        Args:
            pages_data: List of page data
            font_metrics: Font usage statistics
            filename: Original filename
            
        Returns:
            Document title string
        """
        if not pages_data:
            return self._clean_filename(filename)
        
        first_page = pages_data[0]
        
        # Look for the largest text on the first page
        largest_size = 0
        title_candidates = []
        
        for block in first_page.get("blocks", []):
            for span in block.get("spans", []):
                text = span["text"].strip()
                size = span["size"]
                
                if (len(text) >= 5 and len(text) <= 100 and 
                    size >= largest_size and
                    not self._is_likely_header_footer(text, first_page)):
                    
                    if size > largest_size:
                        largest_size = size
                        title_candidates = [text]
                    elif size == largest_size:
                        title_candidates.append(text)
        
        if title_candidates:
            # Choose the first substantial title candidate
            for candidate in title_candidates:
                if len(candidate.split()) >= 2:  # Prefer multi-word titles
                    return candidate
            return title_candidates[0]
        
        # Fallback to filename
        return self._clean_filename(filename)
    
    def _calculate_font_thresholds(self, font_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate font size thresholds for heading classification"""
        all_sizes = []
        
        for font_data in font_metrics.values():
            all_sizes.extend(font_data["sizes"])
        
        if not all_sizes:
            # Default thresholds if no font data
            return {"h1": 16.0, "h2": 14.0, "h3": 12.0, "body": 10.0}
        
        all_sizes.sort(reverse=True)
        
        # Calculate percentiles for thresholds
        n = len(all_sizes)
        
        # H1: Top 5% of font sizes
        h1_threshold = all_sizes[max(0, int(n * 0.05))]
        
        # H2: Top 15% of font sizes  
        h2_threshold = all_sizes[max(0, int(n * 0.15))]
        
        # H3: Top 30% of font sizes
        h3_threshold = all_sizes[max(0, int(n * 0.30))]
        
        # Body: Median font size
        body_threshold = all_sizes[n // 2]
        
        return {
            "h1": max(h1_threshold, body_threshold + 4),  # At least 4pt larger than body
            "h2": max(h2_threshold, body_threshold + 2),  # At least 2pt larger than body
            "h3": max(h3_threshold, body_threshold + 1),  # At least 1pt larger than body
            "body": body_threshold
        }
    
    def _classify_page_headings(self, page_data: Dict, font_metrics: Dict, thresholds: Dict) -> List[Dict[str, Any]]:
        """Classify headings on a single page"""
        headings = []
        page_num = page_data["page_number"]
        
        for block in page_data.get("blocks", []):
            text = block["text"].strip()
            
            if not self._is_potential_heading(text):
                continue
            
            # Get the largest font size in this block
            max_size = self._get_max_font_size(block)
            
            # Check if block has bold text
            has_bold = self._has_bold_text(block)
            
            # Apply classification rules
            heading_type = self._classify_text_as_heading(
                text, max_size, has_bold, thresholds
            )
            
            if heading_type:
                headings.append({
                    "type": heading_type,
                    "text": text,
                    "page": page_num
                })
        
        return headings
    
    def _is_potential_heading(self, text: str) -> bool:
        """Check if text could be a heading based on basic criteria"""
        if len(text) < self.min_heading_length or len(text) > self.max_heading_length:
            return False
        
        # Skip if it's mostly numbers or special characters
        if len(re.sub(r'[^\w\s]', '', text)) < len(text) * 0.7:
            return False
        
        # Skip if it's a single sentence with ending punctuation
        if text.endswith(('.', '!', '?')) and len(text.split('.')) > 1:
            return False
        
        return True
    
    def _get_max_font_size(self, block: Dict) -> float:
        """Get the maximum font size in a text block"""
        max_size = 0
        for span in block.get("spans", []):
            max_size = max(max_size, span.get("size", 0))
        return max_size
    
    def _has_bold_text(self, block: Dict) -> bool:
        """Check if block contains bold text"""
        for span in block.get("spans", []):
            if span.get("is_bold", False):
                return True
        return False
    
    def _classify_text_as_heading(self, text: str, font_size: float, is_bold: bool, thresholds: Dict) -> Optional[str]:
        """Classify text as H1, H2, H3, or None based on various criteria"""
        
        # Pattern-based classification (highest priority)
        pattern_score = self._get_pattern_score(text)
        
        # Font size classification
        if font_size >= thresholds["h1"]:
            size_score = 3
        elif font_size >= thresholds["h2"]:
            size_score = 2
        elif font_size >= thresholds["h3"]:
            size_score = 1
        else:
            size_score = 0
        
        # Bold text gives extra points
        bold_score = 1 if is_bold else 0
        
        # Combined scoring
        total_score = pattern_score + size_score + bold_score
        
        # Classification thresholds
        if total_score >= 4 or pattern_score >= 2:
            return "H1"
        elif total_score >= 3 or (size_score >= 2 and (pattern_score >= 1 or bold_score >= 1)):
            return "H2"
        elif total_score >= 2 or (size_score >= 1 and (pattern_score >= 1 or bold_score >= 1)):
            return "H3"
        
        return None
    
    def _get_pattern_score(self, text: str) -> int:
        """Get score based on heading patterns"""
        for pattern in self.compiled_patterns:
            if pattern.match(text.strip()):
                return 2  # Strong pattern match
        
        # Check for numbered sections (weaker pattern)
        if re.match(r'^\d+\.?\s+\w+', text.strip()):
            return 1
        
        return 0
    
    def _refine_heading_hierarchy(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Post-process headings to ensure logical hierarchy"""
        if not headings:
            return headings
        
        refined = []
        last_h1_page = 0
        last_h2_page = 0
        
        for heading in headings:
            heading_type = heading["type"]
            page = heading["page"]
            
            # Ensure H2s don't appear before any H1
            if heading_type == "H2" and not any(h["type"] == "H1" for h in refined):
                heading["type"] = "H1"
                heading_type = "H1"
            
            # Ensure H3s don't appear before any H2
            if heading_type == "H3" and not any(h["type"] in ["H1", "H2"] for h in refined):
                heading["type"] = "H2"
                heading_type = "H2"
            
            # Track page numbers for hierarchy validation
            if heading_type == "H1":
                last_h1_page = page
            elif heading_type == "H2":
                last_h2_page = page
            
            refined.append(heading)
        
        return refined
    
    def _is_likely_header_footer(self, text: str, page_data: Dict) -> bool:
        """Check if text is likely a header or footer"""
        # Check for page numbers
        if re.match(r'^\d+$', text.strip()):
            return True
        
        # Check for common header/footer words
        footer_words = ["page", "copyright", "confidential", "draft", "proprietary"]
        return any(word in text.lower() for word in footer_words)
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename to use as title fallback"""
        if not filename:
            return "Untitled Document"
        
        # Remove extension
        title = filename.rsplit('.', 1)[0]
        
        # Replace underscores and hyphens with spaces
        title = re.sub(r'[_-]', ' ', title)
        
        # Capitalize words
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title 

def classify_heading(font_size, font_flags):
    """
    Classify text as heading based on font size and style
    
    Args:
        font_size (float): Font size in points
        font_flags (int): Font style flags (bold, italic, etc.)
        
    Returns:
        str or None: Heading type ("H1", "H2", "H3") or None if not a heading
    """
    # Bold font heuristic - check if bold flag is set
    is_bold = font_flags & 2 != 0
    
    # Font size based classification
    if font_size >= 20:
        return "H1"
    elif font_size >= 16 and is_bold:
        return "H2"
    elif font_size >= 13:
        return "H3"
    
    return None 