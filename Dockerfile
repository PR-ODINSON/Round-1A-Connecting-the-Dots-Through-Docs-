# Adobe India Hackathon 2025 - Challenge 1A: Document Structure Extraction
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyMuPDF (keep minimal for size)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements for better caching
COPY requirements.txt .

# Install Python dependencies (optimized for size and speed)
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache NLTK data (no network access during runtime)
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Download spaCy model (with fallback for offline processing)
RUN python -m spacy download en_core_web_sm --quiet || echo "Warning: spaCy model download failed, will use basic processing"

# Copy the main processing script
COPY process_pdfs.py .
COPY pdf_processor.py .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set Python path and environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the PDF processing script
CMD ["python", "process_pdfs.py"] 