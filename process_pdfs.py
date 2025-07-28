#!/usr/bin/env python3
"""
Adobe India Hackathon 2025 - Challenge 1A: Document Structure Extraction
Main processing script for containerized PDF processing

Requirements:
- Process all PDFs from /app/input directory
- Generate filename.json for each filename.pdf
- Complete processing within 10 seconds for 50-page PDFs
- No network access during runtime
- Output must match schema in output_schema.json
"""

import os
import json
import time
from pathlib import Path
from pdf_processor import PDFProcessor

def main():
    """Main processing function for Adobe Challenge 1A"""
    start_time = time.time()
    
    print("🎯 Adobe India Hackathon 2025 - Challenge 1A")
    print("📄 Starting PDF Document Structure Extraction...")
    
    # Get input and output directories as per challenge requirements
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate input directory exists
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Get all PDF files from input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {input_dir}")
        return
    
    print(f"📂 Found {len(pdf_files)} PDF file(s) to process")
    
    # Process each PDF file
    processed_count = 0
    for pdf_file in pdf_files:
        try:
            file_start_time = time.time()
            print(f"📄 Processing: {pdf_file.name}")
            
            # Extract document structure using our AI-powered processor
            result = processor.process_pdf(pdf_file)
            
            # Create output JSON file with exact schema compliance
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            # Ensure Adobe schema format compliance
            adobe_output = {
                "title": result.get("title", ""),
                "outline": result.get("outline", [])
            }
            
            # Save JSON output
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(adobe_output, f, indent=2, ensure_ascii=False)
            
            file_time = time.time() - file_start_time
            print(f"✅ {pdf_file.name} -> {output_file.name} ({file_time:.2f}s)")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            
            # Create minimal output for failed files to ensure schema compliance
            output_file = output_dir / f"{pdf_file.stem}.json"
            fallback_output = {
                "title": pdf_file.stem.replace("_", " ").replace("-", " ").title(),
                "outline": []
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(fallback_output, f, indent=2, ensure_ascii=False)
    
    total_time = time.time() - start_time
    print(f"\n🎊 Processing Complete!")
    print(f"📊 Processed: {processed_count}/{len(pdf_files)} files")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    
    # Validate 10-second constraint for 50-page PDFs
    if total_time > 10:
        print(f"⚠️  Warning: Processing took {total_time:.2f}s (target: ≤10s for 50-page PDFs)")
    else:
        print(f"✅ Performance target met: {total_time:.2f}s ≤ 10s")

if __name__ == "__main__":
    main() 