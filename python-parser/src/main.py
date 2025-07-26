#!/usr/bin/env python3
"""
Adobe Hackathon - PDF Structure Extraction Service
Main FastAPI application for document structure extraction with comprehensive features
"""

import io
import time
import logging
import traceback
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pdf_parser import PDFParser
from heading_classifier import HeadingClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Response models
class HeadingResponse(BaseModel):
    level: str = Field(..., description="Heading level (H1, H2, H3)")
    text: str = Field(..., description="Heading text content")
    page: int = Field(..., description="Page number where heading appears")

class FontMetrics(BaseModel):
    avg_size: float = Field(..., description="Average font size")
    max_size: float = Field(..., description="Maximum font size")
    min_size: float = Field(..., description="Minimum font size")
    count: int = Field(..., description="Number of instances")

class ProcessingMetadata(BaseModel):
    total_pages: int = Field(..., description="Total number of pages processed")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    font_metrics: Dict[str, FontMetrics] = Field(..., description="Font usage statistics")

class DocumentStructureResponse(BaseModel):
    title: str = Field(..., description="Extracted document title")
    outline: list[HeadingResponse] = Field(..., description="Document outline with detected headings")
    metadata: ProcessingMetadata = Field(..., description="Processing metadata")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    timestamp: float = Field(..., description="Current timestamp")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")

# Global instances
pdf_parser = None
heading_classifier = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global pdf_parser, heading_classifier
    
    logger.info("🚀 Starting PDF Structure Extraction Service...")
    
    # Initialize components
    try:
        pdf_parser = PDFParser()
        heading_classifier = HeadingClassifier()
        logger.info("✅ Components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        raise
    
    # Download required models
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("📚 NLTK models downloaded")
    except Exception as e:
        logger.warning(f"⚠️ NLTK download warning: {e}")
    
    yield
    
    logger.info("🛑 Shutting down PDF Structure Extraction Service...")

# Create FastAPI app
app = FastAPI(
    title="Adobe Hackathon - PDF Structure Extraction Service",
    description="""
    🎯 **Adobe India Hackathon 2025 - Round 1A**
    
    Extract document structure and headings from PDF files with advanced NLP and layout analysis.
    
    ## Features
    - **Smart Heading Detection**: Uses font size, style, and pattern recognition
    - **Title Extraction**: Intelligent document title identification
    - **Font Analytics**: Comprehensive font usage statistics
    - **Performance Metrics**: Processing time and metadata
    - **Robust Error Handling**: Detailed error responses
    
    ## Usage
    Upload a PDF file (≤ 50 pages, ≤ 50MB) to `/extract-headings` endpoint.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint with service information"""
    return HealthResponse(
        status="running",
        message="Adobe Hackathon - PDF Structure Extraction Service",
        timestamp=time.time(),
        service="python-parser",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Detailed health check endpoint"""
    global pdf_parser, heading_classifier
    
    try:
        # Verify components are initialized
        if pdf_parser is None or heading_classifier is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service components not properly initialized"
            )
        
        return HealthResponse(
            status="healthy",
            message="All components operational",
            timestamp=time.time(),
            service="python-parser",
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/extract-headings", response_model=DocumentStructureResponse, tags=["PDF Processing"])
async def extract_headings(
    file: UploadFile = File(..., description="PDF file to process (max 50 pages)")
) -> DocumentStructureResponse:
    """
    Extract document structure and headings from uploaded PDF
    
    **Process:**
    1. Validates PDF file format and size
    2. Extracts text and font information using PyMuPDF
    3. Applies NLP and heuristic analysis for heading classification
    4. Returns structured JSON with title, headings, and metadata
    
    **Returns:**
    - Document title
    - Hierarchical headings (H1, H2, H3) with page numbers
    - Font metrics and processing statistics
    """
    start_time = time.time()
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF document"
        )
    
    try:
        # Read file content
        contents = await file.read()
        
        # Validate file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB
        if len(contents) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is 50MB. Current size: {len(contents) / (1024*1024):.1f}MB"
            )
        
        if len(contents) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file provided"
            )
        
        logger.info(f"📄 Processing PDF: {file.filename} ({len(contents)} bytes)")
        
        # Extract text and layout data
        extraction_result = pdf_parser.extract_text_and_layout(contents)
        if not extraction_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse PDF. File may be corrupted or encrypted."
            )
        
        pages_data = extraction_result["pages"]
        font_metrics = extraction_result["font_metrics"]
        total_pages = extraction_result["total_pages"]
        
        # Validate page count
        if total_pages > 50:
            logger.warning(f"PDF has {total_pages} pages, processed first 50")
        
        # Extract title
        title = heading_classifier.extract_title(pages_data, font_metrics, file.filename)
        
        # Classify headings
        headings = heading_classifier.classify_headings(pages_data, font_metrics)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Format font metrics for response
        formatted_font_metrics = {}
        for font_name, metrics in font_metrics.items():
            formatted_font_metrics[font_name] = FontMetrics(
                avg_size=round(metrics.get("avg_size", 0), 1),
                max_size=round(metrics.get("max_size", 0), 1),
                min_size=round(metrics.get("min_size", 0), 1),
                count=metrics.get("count", 0)
            )
        
        # Create response
        response = DocumentStructureResponse(
            title=title,
            outline=[
                HeadingResponse(
                    level=h["type"],
                    text=h["text"],
                    page=h["page"]
                ) for h in headings
            ],
            metadata=ProcessingMetadata(
                total_pages=total_pages,
                processing_time_ms=round(processing_time_ms, 1),
                font_metrics=formatted_font_metrics
            )
        )
        
        logger.info(f"✅ Successfully processed PDF: {title} | {len(headings)} headings | {processing_time_ms:.1f}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing PDF {file.filename}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal processing error: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc)
        }
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