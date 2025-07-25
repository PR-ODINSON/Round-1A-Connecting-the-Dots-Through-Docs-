#!/usr/bin/env python3
"""
Create a sample PDF file for testing
"""

import fitz  # PyMuPDF

def create_sample_pdf():
    """Create a sample PDF with various heading styles"""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add content with different font sizes to test heading detection
    page.insert_text((50, 100), "Document Title", fontsize=24, color=(0, 0, 0))
    page.insert_text((50, 150), "Chapter 1: Getting Started", fontsize=18, color=(0, 0, 0))
    page.insert_text((50, 200), "1.1 Introduction", fontsize=14, color=(0, 0, 0))
    page.insert_text((50, 250), "This is regular paragraph text that should not be detected as a heading.", fontsize=12, color=(0, 0, 0))
    page.insert_text((50, 300), "1.2 Setup Instructions", fontsize=14, color=(0, 0, 0))
    page.insert_text((50, 350), "Chapter 2: Advanced Topics", fontsize=18, color=(0, 0, 0))
    page.insert_text((50, 400), "2.1 Configuration", fontsize=14, color=(0, 0, 0))
    
    # Save the PDF
    doc.save("sample.pdf")
    doc.close()
    print("✅ Created sample.pdf for testing")

if __name__ == "__main__":
    create_sample_pdf() 