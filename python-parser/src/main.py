#!/usr/bin/env python3
"""
Adobe Hackathon - PDF Structure Extraction Service
Main FastAPI application for document structure extraction
"""

import time
import logging
from typing import Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pdf_parser import PDFParser
from heading_classifier import HeadingClassifier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Structure Extraction Service",
    description="Extract document structure and headings from PDF files",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for NestJS integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
pdf_parser = PDFParser()
heading_classifier = HeadingClassifier()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Adobe Hackathon - PDF Structure Extraction Service",
        "status": "running",
        "timestamp": time.time(),
        "service": "python-parser"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {
            "pdf_parser": "initialized",
            "heading_classifier": "initialized",
            "dependencies": {
                "pymupdf": "available",
                "spacy": "available",
                "nltk": "available"
            }
        }
    }

@app.post("/extract-headings")
async def extract_headings(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract document structure and headings from a PDF file
    
    Args:
        file: PDF file upload
        
    Returns:
        Dict containing document title, headings, and metadata
    """
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.content_type == "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only PDF files are supported."
            )
        
        # Read file content
        pdf_content = await file.read()
        
        if len(pdf_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file provided"
            )
        
        logger.info(f"🔍 Processing PDF: {file.filename} ({len(pdf_content)} bytes)")
        
        # Extract text and layout information
        extraction_result = pdf_parser.extract_text_and_layout(pdf_content)
        
        if not extraction_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to extract content from PDF. File may be corrupted or encrypted."
            )
        
        # Classify headings using layout heuristics
        headings = heading_classifier.classify_headings(
            extraction_result["pages"],
            extraction_result["font_metrics"]
        )
        
        # Extract document title (first large text or filename fallback)
        title = heading_classifier.extract_title(
            extraction_result["pages"],
            extraction_result["font_metrics"],
            file.filename
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        result = {
            "title": title,
            "headings": headings,
            "metadata": {
                "total_pages": extraction_result["total_pages"],
                "processing_time_ms": processing_time,
                "font_metrics": extraction_result["font_metrics"],
                "file_size_bytes": len(pdf_content)
            }
        }
        
        logger.info(f"✅ Successfully processed PDF: {len(headings)} headings found in {processing_time}ms")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing PDF: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 