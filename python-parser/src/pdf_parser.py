#!/usr/bin/env python3
"""
PDF Parser Module
Extracts text, font information, and layout data from PDF files using PyMuPDF
"""

import io
import logging
from typing import Dict, List, Any, Optional
import fitz  # PyMuPDF
    
logger = logging.getLogger(__name__)

class PDFParser:
    """PDF parsing functionality using PyMuPDF"""
    
    def __init__(self):
        """Initialize the PDF parser"""
        self.max_pages = 50  # Hackathon requirement
        
    def extract_text_and_layout(self, pdf_content: bytes) -> Optional[Dict[str, Any]]:
        """
        Extract text and layout information from PDF content
        
        Args:
            pdf_content: Raw PDF file bytes
            
        Returns:
            Dict containing pages data, font metrics, and metadata
        """
        try:
            # Open PDF from bytes
            pdf_stream = io.BytesIO(pdf_content)
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            
            if doc.page_count > self.max_pages:
                logger.warning(f"PDF has {doc.page_count} pages, limiting to {self.max_pages}")
            
            pages_data = []
            font_metrics = {}
            total_chars = 0
            
            # Process each page up to the limit
            for page_num in range(min(doc.page_count, self.max_pages)):
                page = doc[page_num]
                page_data = self._extract_page_data(page, page_num + 1)
                pages_data.append(page_data)
                
                # Accumulate font metrics
                for font_name, metrics in page_data["font_metrics"].items():
                    if font_name not in font_metrics:
                        font_metrics[font_name] = {
                            "sizes": [],
                            "count": 0,
                            "total_chars": 0
                        }
                    
                    font_metrics[font_name]["sizes"].extend(metrics["sizes"])
                    font_metrics[font_name]["count"] += metrics["count"]
                    font_metrics[font_name]["total_chars"] += metrics["total_chars"]
                
                total_chars += len(page_data["text"])
            
            doc.close()
            
            # Calculate average font sizes
            for font_name in font_metrics:
                sizes = font_metrics[font_name]["sizes"]
                if sizes:
                    font_metrics[font_name]["avg_size"] = sum(sizes) / len(sizes)
                    font_metrics[font_name]["max_size"] = max(sizes)
                    font_metrics[font_name]["min_size"] = min(sizes)
                else:
                    font_metrics[font_name]["avg_size"] = 12.0
                    font_metrics[font_name]["max_size"] = 12.0
                    font_metrics[font_name]["min_size"] = 12.0
            
            logger.info(f"📊 Extracted {len(pages_data)} pages, {total_chars} characters, {len(font_metrics)} fonts")
            
            return {
                "pages": pages_data,
                "font_metrics": font_metrics,
                "total_pages": len(pages_data),
                "total_characters": total_chars
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return None
    
    def _extract_page_data(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """
        Extract detailed information from a single page
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-indexed)
            
        Returns:
            Dict containing page text, blocks, and font metrics
        """
        # Get text blocks with formatting information
        blocks = page.get_text("dict")["blocks"]
        
        page_text = ""
        text_blocks = []
        font_metrics = {}
        
        for block in blocks:
            if "lines" in block:  # Text block
                block_data = self._process_text_block(block, font_metrics)
                text_blocks.append(block_data)
                page_text += block_data["text"] + "\n"
        
        return {
            "page_number": page_num,
            "text": page_text.strip(),
            "blocks": text_blocks,
            "font_metrics": font_metrics,
            "page_rect": {
                "width": page.rect.width,
                "height": page.rect.height
            }
        }
    
    def _process_text_block(self, block: Dict, font_metrics: Dict) -> Dict[str, Any]:
        """
        Process a text block and extract font information
        
        Args:
            block: Text block from PyMuPDF
            font_metrics: Dictionary to accumulate font statistics
            
        Returns:
            Dict containing block text and formatting info
        """
        block_text = ""
        spans_data = []
        
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text:
                    continue
                
                # Extract font information
                font_name = span.get("font", "unknown")
                font_size = span.get("size", 12.0)
                font_flags = span.get("flags", 0)
                
                # Determine if text is bold/italic based on flags or font name
                is_bold = bool(font_flags & 2**4) or "bold" in font_name.lower()
                is_italic = bool(font_flags & 2**1) or "italic" in font_name.lower()
                
                # Create canonical font identifier
                font_key = f"{font_name}"
                if is_bold:
                    font_key += "-Bold"
                if is_italic:
                    font_key += "-Italic"
                
                # Accumulate font metrics
                if font_key not in font_metrics:
                    font_metrics[font_key] = {
                        "sizes": [],
                        "count": 0,
                        "total_chars": 0
                    }
                
                font_metrics[font_key]["sizes"].append(font_size)
                font_metrics[font_key]["count"] += 1
                font_metrics[font_key]["total_chars"] += len(text)
                
                spans_data.append({
                    "text": text,
                    "font": font_key,
                    "size": font_size,
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "bbox": span.get("bbox", [0, 0, 0, 0])
                })
                
                block_text += text + " "
        
        return {
            "text": block_text.strip(),
            "spans": spans_data,
            "bbox": block.get("bbox", [0, 0, 0, 0])
        } 