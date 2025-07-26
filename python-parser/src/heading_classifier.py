#!/usr/bin/env python3
"""
Heading Classifier Module
Uses font size, style, position heuristics, and NLP to classify text as H1, H2, or H3 headings
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# Import NLP libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available, using basic text processing")

try:
    import spacy
    # Try to load English model
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except OSError:
        SPACY_AVAILABLE = False
        logging.warning("spaCy English model not found, using basic text processing")
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available, using basic text processing")

logger = logging.getLogger(__name__)

class HeadingClassifier:
    """Classify text as headings using layout, font, and NLP heuristics"""
    
    def __init__(self):
        """Initialize the heading classifier"""
        self.heading_patterns = [
            # Chapter/Section patterns
            r'^(chapter|section|part)\s+\d+',
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
            r'^\d+\.\d+\.?\s+[A-Z]',  # "1.1 Overview" or "1.1. Overview"
            r'^\d+\.\d+\.\d+\.?\s+[A-Z]',  # "1.1.1 Details"
            
            # Roman numerals
            r'^[IVX]+\.?\s+[A-Z]',  # "I. Introduction", "II Overview"
            
            # Letter enumeration
            r'^[A-Z]\.?\s+[A-Z]',  # "A. Introduction", "B Overview"
            
            # Common heading words
            r'^(introduction|conclusion|summary|overview|background|methodology|results|discussion|references)',
            r'^(abstract|acknowledgments?|appendix|bibliography|glossary)',
            r'^(table\s+of\s+contents?|contents?)',
            r'^(executive\s+summary|literature\s+review|case\s+study)',
            
            # All caps (potential headings) - more restrictive
            r'^[A-Z\s\-]{4,50}$',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.heading_patterns]
        
        # Common heading keywords
        self.heading_keywords = {
            'introduction', 'conclusion', 'summary', 'overview', 'background',
            'methodology', 'methods', 'results', 'discussion', 'analysis',
            'abstract', 'acknowledgments', 'appendix', 'bibliography', 'glossary',
            'contents', 'preface', 'foreword', 'executive', 'literature',
            'review', 'study', 'research', 'findings', 'recommendations',
            'implementation', 'evaluation', 'assessment', 'framework',
            'approach', 'design', 'architecture', 'system', 'model'
        }
        
        # Initialize stopwords if NLTK is available
        self.stopwords = set()
        if NLTK_AVAILABLE:
            try:
                self.stopwords = set(stopwords.words('english'))
            except LookupError:
                logger.warning("NLTK stopwords not downloaded")
        
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
        
        # Analyze document structure for better classification
        document_stats = self._analyze_document_structure(pages_data)
        
        for page_data in pages_data:
            page_headings = self._classify_page_headings(
                page_data, 
                font_metrics, 
                size_thresholds,
                document_stats
            )
            headings.extend(page_headings)
        
        # Post-process headings to ensure hierarchy makes sense
        headings = self._refine_heading_hierarchy(headings)
        
        # Apply NLP-based filtering if available
        if SPACY_AVAILABLE or NLTK_AVAILABLE:
            headings = self._apply_nlp_filtering(headings)
        
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
                    not self._is_likely_header_footer(text, first_page) and
                    not self._is_page_number(text)):
                    
                    if size > largest_size:
                        largest_size = size
                        title_candidates = [text]
                    elif size == largest_size:
                        title_candidates.append(text)
        
        # Filter title candidates using NLP if available
        if title_candidates:
            best_title = self._select_best_title(title_candidates)
            if best_title:
                return best_title
        
        # Fallback to filename
        return self._clean_filename(filename)
    
    def _analyze_document_structure(self, pages_data: List[Dict]) -> Dict[str, Any]:
        """Analyze overall document structure for better classification"""
        stats = {
            "total_text_blocks": 0,
            "avg_line_length": 0,
            "common_fonts": {},
            "font_size_distribution": [],
            "has_numbered_sections": False,
            "has_table_of_contents": False
        }
        
        all_text_lengths = []
        font_usage = defaultdict(int)
        all_font_sizes = []
        
        for page_data in pages_data:
            for block in page_data.get("blocks", []):
                stats["total_text_blocks"] += 1
                text = block["text"].strip()
                all_text_lengths.append(len(text))
                
                # Check for numbered sections
                if re.match(r'^\d+\.?\d*\.?\s+\w+', text):
                    stats["has_numbered_sections"] = True
                
                # Check for table of contents
                if re.search(r'table\s+of\s+contents?|contents?', text, re.IGNORECASE):
                    stats["has_table_of_contents"] = True
                
                # Analyze fonts
                for span in block.get("spans", []):
                    font = span.get("font", "unknown")
                    font_usage[font] += 1
                    all_font_sizes.append(span.get("size", 12))
        
        if all_text_lengths:
            stats["avg_line_length"] = sum(all_text_lengths) / len(all_text_lengths)
        
        stats["common_fonts"] = dict(sorted(font_usage.items(), key=lambda x: x[1], reverse=True)[:5])
        stats["font_size_distribution"] = sorted(set(all_font_sizes), reverse=True)
        
        return stats
    
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
        
        # More sophisticated threshold calculation
        # H1: Top 3% of font sizes (more exclusive)
        h1_threshold = all_sizes[max(0, int(n * 0.03))]
        
        # H2: Top 10% of font sizes  
        h2_threshold = all_sizes[max(0, int(n * 0.10))]
        
        # H3: Top 25% of font sizes
        h3_threshold = all_sizes[max(0, int(n * 0.25))]
        
        # Body: 70th percentile (most common text size)
        body_threshold = all_sizes[max(0, int(n * 0.70))]
        
        return {
            "h1": max(h1_threshold, body_threshold + 4),  # At least 4pt larger than body
            "h2": max(h2_threshold, body_threshold + 2),  # At least 2pt larger than body
            "h3": max(h3_threshold, body_threshold + 1),  # At least 1pt larger than body
            "body": body_threshold
        }
    
    def _classify_page_headings(self, page_data: Dict, font_metrics: Dict, 
                              thresholds: Dict, document_stats: Dict) -> List[Dict[str, Any]]:
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
            
            # Check positioning (approximate)
            is_isolated = self._is_text_isolated(block, page_data)
            
            # Apply classification rules
            heading_type = self._classify_text_as_heading(
                text, max_size, has_bold, thresholds, is_isolated, document_stats
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
        alpha_chars = len(re.sub(r'[^\w\s]', '', text))
        if alpha_chars < len(text) * 0.6:  # At least 60% alphanumeric
            return False
        
        # Skip if it's a single sentence with ending punctuation (unless it's a question)
        if text.endswith(('.', '!')) and len(text.split('.')) > 1:
            return False
        
        # Skip very long sentences (likely body text)
        if len(text.split()) > 15 and text.endswith('.'):
            return False
        
        # Skip obvious non-headings
        if re.match(r'^\s*(figure|table|chart|graph)\s+\d+', text, re.IGNORECASE):
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
    
    def _is_text_isolated(self, block: Dict, page_data: Dict) -> bool:
        """Check if text block appears isolated (surrounded by whitespace)"""
        # Simple heuristic: check if block is shorter than average
        text_length = len(block["text"])
        
        # Get average block length on this page
        total_length = 0
        block_count = 0
        for other_block in page_data.get("blocks", []):
            total_length += len(other_block["text"])
            block_count += 1
        
        if block_count == 0:
            return False
            
        avg_length = total_length / block_count
        return text_length < avg_length * 0.5  # Much shorter than average
    
    def _classify_text_as_heading(self, text: str, font_size: float, is_bold: bool, 
                                thresholds: Dict, is_isolated: bool, document_stats: Dict) -> Optional[str]:
        """Classify text as H1, H2, H3, or None based on various criteria"""
        
        # Pattern-based classification (highest priority)
        pattern_score = self._get_pattern_score(text, document_stats)
        
        # Font size classification
        if font_size >= thresholds["h1"]:
            size_score = 3
        elif font_size >= thresholds["h2"]:
            size_score = 2
        elif font_size >= thresholds["h3"]:
            size_score = 1
        else:
            size_score = 0
        
        # Additional scoring factors
        bold_score = 1 if is_bold else 0
        isolation_score = 1 if is_isolated else 0
        keyword_score = self._get_keyword_score(text)
        
        # Combined scoring with weights
        total_score = (pattern_score * 2) + size_score + bold_score + isolation_score + keyword_score
        
        # Enhanced classification thresholds
        if total_score >= 6 or pattern_score >= 2:
            return "H1"
        elif total_score >= 4 or (size_score >= 2 and pattern_score >= 1):
            return "H2"
        elif total_score >= 3 or (size_score >= 1 and (pattern_score >= 1 or keyword_score >= 1)):
            return "H3"
        
        return None
    
    def _get_pattern_score(self, text: str, document_stats: Dict) -> int:
        """Get score based on heading patterns"""
        for pattern in self.compiled_patterns:
            if pattern.match(text.strip()):
                return 2  # Strong pattern match
        
        # Check for numbered sections (enhanced)
        if re.match(r'^\d+\.?\s+\w+', text.strip()):
            return 2 if document_stats.get("has_numbered_sections") else 1
        
        # Check for sub-numbered sections
        if re.match(r'^\d+\.\d+\.?\s+\w+', text.strip()):
            return 1
        
        return 0
    
    def _get_keyword_score(self, text: str) -> int:
        """Get score based on heading keywords"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # Remove stopwords if NLTK is available
        if self.stopwords:
            words = [w for w in words if w not in self.stopwords]
        
        # Check for heading keywords
        keyword_matches = sum(1 for word in words if word in self.heading_keywords)
        
        if keyword_matches >= 2:
            return 2
        elif keyword_matches >= 1:
            return 1
        
        return 0
    
    def _refine_heading_hierarchy(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Post-process headings to ensure logical hierarchy"""
        if not headings:
            return headings
        
        refined = []
        h1_count = 0
        h2_count = 0
        last_heading_type = None
        
        for heading in headings:
            heading_type = heading["type"]
            page = heading["page"]
            text = heading["text"]
            
            # Ensure reasonable distribution of heading types
            if heading_type == "H1":
                h1_count += 1
                # If too many H1s, demote some to H2
                if h1_count > 10 and len(text) < 30:  # Short titles might be H2
                    heading_type = "H2"
                    heading["type"] = "H2"
            elif heading_type == "H2":
                h2_count += 1
                # Ensure H2s don't appear before any H1 (unless it's a very structured document)
                if h1_count == 0 and h2_count == 1:
                    heading_type = "H1"
                    heading["type"] = "H1"
                    h1_count += 1
            elif heading_type == "H3":
                # Ensure H3s don't appear before any H2
                if h1_count == 0 and h2_count == 0:
                    heading_type = "H2"
                    heading["type"] = "H2"
                    h2_count += 1
            
            last_heading_type = heading_type
            refined.append(heading)
        
        return refined
    
    def _apply_nlp_filtering(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply NLP-based filtering to improve heading quality"""
        if not SPACY_AVAILABLE and not NLTK_AVAILABLE:
            return headings
        
        filtered_headings = []
        
        for heading in headings:
            text = heading["text"]
            
            # Use spaCy for more sophisticated analysis if available
            if SPACY_AVAILABLE:
                doc = nlp(text)
                
                # Filter out texts that are predominantly proper nouns (might be names/places)
                proper_nouns = [token for token in doc if token.pos_ == "PROPN"]
                if len(proper_nouns) > len(doc) * 0.8 and len(doc) > 3:
                    continue
                
                # Check for meaningful content
                content_tokens = [token for token in doc if not token.is_stop and not token.is_punct]
                if len(content_tokens) == 0:
                    continue
            
            # Basic NLTK filtering
            elif NLTK_AVAILABLE:
                try:
                    tokens = word_tokenize(text.lower())
                    content_tokens = [t for t in tokens if t.isalpha() and t not in self.stopwords]
                    if len(content_tokens) == 0:
                        continue
                except:
                    pass  # Continue without NLTK filtering if there's an error
            
            filtered_headings.append(heading)
        
        return filtered_headings
    
    def _select_best_title(self, candidates: List[str]) -> Optional[str]:
        """Select the best title from candidates using NLP"""
        if not candidates:
            return None
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Score candidates
        scored_candidates = []
        
        for candidate in candidates:
            score = 0
            
            # Prefer multi-word titles
            words = candidate.split()
            if len(words) >= 2:
                score += 2
            elif len(words) >= 3:
                score += 3
            
            # Prefer titles without excessive punctuation
            punct_ratio = sum(1 for c in candidate if not c.isalnum() and c != ' ') / len(candidate)
            if punct_ratio < 0.1:
                score += 1
            
            # Prefer titles that aren't all caps (unless short)
            if not candidate.isupper() or len(candidate) <= 10:
                score += 1
            
            # Use NLP scoring if available
            if SPACY_AVAILABLE:
                doc = nlp(candidate)
                # Prefer titles with nouns
                nouns = [token for token in doc if token.pos_ in ["NOUN", "PROPN"]]
                score += len(nouns)
            
            scored_candidates.append((score, candidate))
        
        # Return the highest scoring candidate
        scored_candidates.sort(reverse=True)
        return scored_candidates[0][1]
    
    def _is_likely_header_footer(self, text: str, page_data: Dict) -> bool:
        """Check if text is likely a header or footer"""
        # Check for page numbers
        if re.match(r'^\d+$', text.strip()):
            return True
        
        # Check for common header/footer words
        footer_words = ["page", "copyright", "confidential", "draft", "proprietary", "©"]
        return any(word in text.lower() for word in footer_words)
    
    def _is_page_number(self, text: str) -> bool:
        """Check if text is just a page number"""
        return re.match(r'^\s*\d+\s*$', text) is not None
    
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