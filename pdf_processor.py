#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1A: Optimized PDF Processor
High-performance document structure extraction with AI-powered heading classification

Optimized for:
- ≤10 seconds processing time for 50-page PDFs
- ≤200MB model size constraint
- No network access during runtime
- Exact Adobe schema compliance
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import fitz  # PyMuPDF

# Import NLP libraries with fallback handling
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import stopwords
    NLTK_AVAILABLE = True
    try:
        STOP_WORDS = set(stopwords.words('english'))
    except:
        STOP_WORDS = set()
except ImportError:
    NLTK_AVAILABLE = False
    STOP_WORDS = set()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """High-performance PDF processor optimized for Adobe Challenge 1A"""
    
    def __init__(self):
        """Initialize the PDF processor with optimized settings"""
        self.max_pages = 50  # Challenge constraint
        
        # Optimized heading patterns for speed
        self.heading_patterns = [
            # High-priority patterns (most common)
            re.compile(r'^\d+\.?\s+[A-Z]', re.IGNORECASE),  # "1. Introduction"
            re.compile(r'^\d+\.\d+\.?\s+[A-Z]', re.IGNORECASE),  # "1.1 Overview"
            re.compile(r'^(chapter|section|part)\s+\d+', re.IGNORECASE),
            
            # Medium-priority patterns
            re.compile(r'^[IVX]+\.?\s+[A-Z]', re.IGNORECASE),  # Roman numerals
            re.compile(r'^[A-Z]\.?\s+[A-Z]', re.IGNORECASE),  # Letter enumeration
            
            # Common heading keywords (optimized set)
            re.compile(r'^(introduction|conclusion|summary|overview|background|abstract|references)', re.IGNORECASE),
            re.compile(r'^(acknowledgments?|appendix|bibliography|contents?)', re.IGNORECASE),
        ]
        
        # Optimized keyword set (reduced for performance)
        self.heading_keywords = {
            'introduction', 'conclusion', 'summary', 'overview', 'background',
            'abstract', 'references', 'acknowledgments', 'appendix', 'contents',
            'methodology', 'results', 'discussion', 'analysis'
        }
        
        logger.info(f"PDF Processor initialized (spaCy: {SPACY_AVAILABLE}, NLTK: {NLTK_AVAILABLE})")
    
    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file and extract document structure
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with title and outline following Adobe schema
        """
        try:
            # Open PDF with error handling
            doc = fitz.open(str(pdf_path))
            
            # Limit pages for performance (Challenge constraint)
            page_count = min(doc.page_count, self.max_pages)
            
            if page_count == 0:
                return {"title": "", "outline": []}
            
            # Extract text and analyze structure efficiently
            pages_data = []
            font_info = {}
            
            for page_num in range(page_count):
                page = doc[page_num]
                page_data = self._extract_page_data_fast(page, page_num)
                pages_data.append(page_data)
                
                # Collect font information for thresholds
                for block in page_data.get("blocks", []):
                    for span in block.get("spans", []):
                        font_size = span.get("size", 12)
                        font_name = span.get("font", "default")
                        
                        if font_name not in font_info:
                            font_info[font_name] = []
                        font_info[font_name].append(font_size)
            
            doc.close()
            
            # Calculate font thresholds efficiently
            thresholds = self._calculate_thresholds_fast(font_info)
            
            # Extract title (first large text or filename fallback)
            title = self._extract_title_fast(pages_data, pdf_path)
            
            # Classify headings with optimized algorithm
            outline = self._classify_headings_fast(pages_data, thresholds)
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            # Return minimal valid output for schema compliance
            return {
                "title": pdf_path.stem.replace("_", " ").replace("-", " ").title(),
                "outline": []
            }
    
    def _extract_page_data_fast(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """Fast page data extraction optimized for performance"""
        blocks = page.get_text("dict")["blocks"]
        
        text_blocks = []
        for block in blocks:
            if "lines" not in block:
                continue
            
            block_text = ""
            spans_data = []
            
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    
                    # Extract essential font information only
                    font_size = span.get("size", 12.0)
                    font_flags = span.get("flags", 0)
                    font_name = span.get("font", "unknown")
                    
                    is_bold = bool(font_flags & 16) or "bold" in font_name.lower()
                    
                    spans_data.append({
                        "text": text,
                        "size": font_size,
                        "font": font_name,
                        "is_bold": is_bold
                    })
                    
                    block_text += text + " "
            
            if block_text.strip():
                text_blocks.append({
                    "text": block_text.strip(),
                    "spans": spans_data
                })
        
        return {
            "page_number": page_num + 1,  # 1-indexed for output
            "blocks": text_blocks
        }
    
    def _calculate_thresholds_fast(self, font_info: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate font size thresholds efficiently"""
        all_sizes = []
        for sizes in font_info.values():
            all_sizes.extend(sizes)
        
        if not all_sizes:
            return {"h1": 16.0, "h2": 14.0, "h3": 12.0, "body": 10.0}
        
        all_sizes.sort(reverse=True)
        n = len(all_sizes)
        
        # Fast percentile calculation
        h1_idx = max(0, int(n * 0.05))  # Top 5%
        h2_idx = max(0, int(n * 0.15))  # Top 15%
        h3_idx = max(0, int(n * 0.30))  # Top 30%
        body_idx = n // 2  # Median
        
        return {
            "h1": all_sizes[h1_idx],
            "h2": all_sizes[h2_idx],
            "h3": all_sizes[h3_idx],
            "body": all_sizes[body_idx]
        }
    
    def _extract_title_fast(self, pages_data: List[Dict], pdf_path: Path) -> str:
        """Fast title extraction"""
        if not pages_data:
            return self._clean_filename(pdf_path.name)
        
        # Look for largest text on first page
        first_page = pages_data[0]
        largest_size = 0
        title_candidate = ""
        
        for block in first_page.get("blocks", [])[:5]:  # Check only first 5 blocks for speed
            for span in block.get("spans", []):
                text = span["text"].strip()
                size = span["size"]
                
                if (len(text) >= 5 and len(text) <= 100 and 
                    size > largest_size and
                    not self._is_page_number(text)):
                    
                    largest_size = size
                    title_candidate = text
        
        return title_candidate if title_candidate else self._clean_filename(pdf_path.name)
    
    def _classify_headings_fast(self, pages_data: List[Dict], thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
        """Fast heading classification optimized for performance"""
        headings = []
        
        for page_data in pages_data:
            page_num = page_data["page_number"]
            
            for block in page_data.get("blocks", []):
                text = block["text"].strip()
                
                # Quick filtering
                if not self._is_potential_heading_fast(text):
                    continue
                
                # Get maximum font size in block
                max_size = max((span.get("size", 12) for span in block.get("spans", [])), default=12)
                
                # Check for bold text
                has_bold = any(span.get("is_bold", False) for span in block.get("spans", []))
                
                # Fast classification
                heading_level = self._classify_text_fast(text, max_size, has_bold, thresholds)
                
                if heading_level:
                    headings.append({
                        "level": heading_level,
                        "text": text,
                        "page": page_num
                    })
        
        # Post-process for hierarchy (simplified for speed)
        return self._refine_hierarchy_fast(headings)
    
    def _is_potential_heading_fast(self, text: str) -> bool:
        """Fast heading potential check"""
        if len(text) < 3 or len(text) > 200:
            return False
        
        # Skip obvious non-headings
        if text.endswith('.') and len(text.split()) > 15:
            return False
        
        if re.match(r'^\s*(figure|table|chart|graph)\s+\d+', text, re.IGNORECASE):
            return False
        
        return True
    
    def _classify_text_fast(self, text: str, font_size: float, is_bold: bool, thresholds: Dict[str, float]) -> Optional[str]:
        """Fast text classification with optimized scoring"""
        # Pattern score (fast check)
        pattern_score = 0
        for pattern in self.heading_patterns[:4]:  # Check only top patterns for speed
            if pattern.match(text.strip()):
                pattern_score = 2
                break
        
        # Font size score
        if font_size >= thresholds["h1"]:
            size_score = 3
        elif font_size >= thresholds["h2"]:
            size_score = 2
        elif font_size >= thresholds["h3"]:
            size_score = 1
        else:
            size_score = 0
        
        # Keyword score (simplified)
        keyword_score = 1 if any(keyword in text.lower() for keyword in self.heading_keywords) else 0
        
        # Bold score
        bold_score = 1 if is_bold else 0
        
        # Total score
        total_score = pattern_score + size_score + bold_score + keyword_score
        
        # Classification
        if total_score >= 4:
            return "H1"
        elif total_score >= 3:
            return "H2"
        elif total_score >= 2:
            return "H3"
        
        return None
    
    def _refine_hierarchy_fast(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fast hierarchy refinement"""
        if not headings:
            return headings
        
        # Simple hierarchy fix: ensure first heading is H1
        if headings and headings[0]["level"] not in ["H1"]:
            headings[0]["level"] = "H1"
        
        return headings
    
    def _is_page_number(self, text: str) -> bool:
        """Check if text is just a page number"""
        return re.match(r'^\s*\d+\s*$', text) is not None
    
    def _clean_filename(self, filename: str) -> str:
        """Clean filename for title fallback"""
        if not filename:
            return "Untitled Document"
        
        # Remove extension and clean up
        title = filename.rsplit('.', 1)[0]
        title = re.sub(r'[_-]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Capitalize words
        return ' '.join(word.capitalize() for word in title.split()) or "Untitled Document" 