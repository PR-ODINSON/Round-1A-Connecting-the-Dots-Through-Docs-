#!/usr/bin/env python3
"""
Test script for the PDF Structure Extraction Service
"""

import requests
import io
import fitz  # PyMuPDF

def create_sample_pdf():
    """Create a simple sample PDF with headings for testing"""
    doc = fitz.open()
    page = doc.new_page()
    
    # Add some sample text with different font sizes
    page.insert_text((50, 100), "Sample Document Title", fontsize=24, color=(0, 0, 0))
    page.insert_text((50, 150), "Chapter 1: Introduction", fontsize=18, color=(0, 0, 0))
    page.insert_text((50, 200), "1.1 Overview", fontsize=14, color=(0, 0, 0))
    page.insert_text((50, 250), "This is some regular text content.", fontsize=12, color=(0, 0, 0))
    page.insert_text((50, 300), "1.2 Purpose", fontsize=14, color=(0, 0, 0))
    page.insert_text((50, 350), "Chapter 2: Implementation", fontsize=18, color=(0, 0, 0))
    
    # Save to bytes
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        print("✅ Health check passed!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    print()

def test_extract_headings():
    """Test the extract-headings endpoint"""
    print("🔍 Testing PDF extraction endpoint...")
    
    # Create sample PDF
    pdf_bytes = create_sample_pdf()
    
    # Send request
    files = {"file": ("sample.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    response = requests.post("http://localhost:8000/extract-headings", files=files)
    
    if response.status_code == 200:
        print("✅ PDF extraction successful!")
        result = response.json()
        print(f"Title: {result['title']}")
        print(f"Found {len(result['headings'])} headings:")
        for heading in result['headings']:
            print(f"  - {heading['type']}: {heading['text']} (Page {heading['page']})")
    else:
        print(f"❌ PDF extraction failed: {response.status_code}")
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("🚀 Testing PDF Structure Extraction Service")
    print("=" * 50)
    
    try:
        test_health_check()
        test_extract_headings()
        print("🎉 All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to service. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 