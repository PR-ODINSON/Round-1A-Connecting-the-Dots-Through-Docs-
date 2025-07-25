#!/usr/bin/env python3
"""
Adobe Hackathon - PDF Structure Extraction Service
Main FastAPI application for document structure extraction
"""

import time
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pdf_parser import parse_pdf

app = FastAPI(
    title="PDF Structure Extraction Service",
    description="Extract document structure and headings from PDF files",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {
        "message": "Adobe Hackathon - PDF Structure Extraction Service",
        "status": "running",
        "timestamp": time.time(),
        "service": "python-parser"
    }

@app.post("/extract-headings")
async def extract_headings(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        result = parse_pdf(contents)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 