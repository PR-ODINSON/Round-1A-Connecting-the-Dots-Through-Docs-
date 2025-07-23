# Adobe Hackathon - Document Structure Extraction Backend

🎯 **Round 1A: Document Structure Extraction** - Backend implementation for the Adobe India Hackathon (Connecting the Dots).

## 📋 Overview

This backend system extracts structural outlines from PDF documents (≤ 50 pages) and returns them in JSON format, including:
- Document title
- All detected H1, H2, and H3 headings with their corresponding page numbers
- Processing metadata and font metrics

## 🏗️ Architecture

```
┌─────────────────┐     HTTP/REST     ┌─────────────────┐
│   NestJS API    │ ◄────────────────► │  Python Parser  │
│   (Port 3000)   │                   │   (Port 8000)   │
│                 │                   │                 │
│ • File Upload   │                   │ • PyMuPDF       │
│ • Validation    │                   │ • spaCy/NLTK    │
│ • API Docs      │                   │ • Heuristics    │
└─────────────────┘                   └─────────────────┘
```

### 🔙 **NestJS Backend** (`nestjs-backend/`)
- **Framework**: NestJS (Node.js + TypeScript)
- **Responsibilities**:
  - Accept PDF uploads via REST API (`POST /pdf-extraction/parse-pdf`)
  - Validate file type and size (≤ 50MB)
  - Forward PDF to Python microservice
  - Return structured JSON to client
  - Provide API documentation via Swagger

### 🐍 **Python Microservice** (`python-parser/`)
- **Framework**: FastAPI
- **Tools**: `PyMuPDF`, `spaCy`, `NLTK`
- **Responsibilities**:
  - Extract text, font size, position, indentation from PDF
  - Apply heuristics to classify headings as H1/H2/H3
  - Return structured JSON with document title and headings

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB RAM recommended
- AMD64 compatible system

### 1. Clone and Start
```bash
# Clone the repository
cd /path/to/your/workspace

# Start all services
npm run dev
# or directly:
docker-compose up --build
```

### 2. Services will be available at:
- **NestJS API**: http://localhost:3000
- **API Documentation**: http://localhost:3000/api
- **Python Service**: http://localhost:8000
- **Python Docs**: http://localhost:8000/docs

### 3. Test the API
```bash
# Upload a PDF file
curl -X POST \
  http://localhost:3000/pdf-extraction/parse-pdf \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.pdf"
```

## 📚 API Documentation

### Main Endpoint: `POST /pdf-extraction/parse-pdf`

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: PDF file (≤ 50MB, ≤ 50 pages)

**Response:**
```json
{
  "title": "Sample Document Title",
  "headings": [
    {
      "type": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "type": "H2", 
      "text": "Problem Statement",
      "page": 2
    },
    {
      "type": "H3",
      "text": "Scope and Limitations", 
      "page": 3
    }
  ],
  "metadata": {
    "totalPages": 25,
    "processingTimeMs": 1250,
    "fontMetrics": {
      "Arial-Bold": {
        "avg_size": 16.5,
        "max_size": 20.0,
        "min_size": 14.0,
        "count": 15
      }
    }
  }
}
```

### Health Check Endpoints:
- `GET /` - Simple health check
- `GET /health` - Detailed service status
- `GET /api` - Interactive API documentation

## 🧠 Heading Classification Algorithm

The system uses sophisticated heuristics to classify headings:

### 1. **Font Size Analysis**
- Calculates percentile-based thresholds from document fonts
- H1: Top 5% of font sizes (minimum 4pt larger than body)
- H2: Top 15% of font sizes (minimum 2pt larger than body)  
- H3: Top 30% of font sizes (minimum 1pt larger than body)

### 2. **Pattern Recognition**
- Chapter/Section patterns: `"Chapter 1"`, `"1. Introduction"`
- Numbered sections: `"1.1 Overview"`, `"1.1.1 Details"`
- Common heading words: `"Introduction"`, `"Summary"`, `"Conclusion"`
- All-caps text (potential headings)

### 3. **Formatting Detection**
- Bold text identification
- Font family analysis
- Position and indentation

### 4. **Scoring System**
- Combines pattern matching (0-2 points)
- Font size classification (0-3 points)
- Bold formatting (0-1 point)
- Classification thresholds: H1 (≥4 points), H2 (≥3 points), H3 (≥2 points)

### 5. **Post-Processing**
- Ensures logical hierarchy (H2s follow H1s, H3s follow H2s)
- Filters out headers/footers and page numbers
- Validates heading length and content

## 🐳 Docker Configuration

### Services:
- **nestjs-backend**: NestJS API server
- **python-parser**: FastAPI PDF processing service

### Networks:
- Internal bridge network for service communication
- Health checks for service monitoring

### Development vs Production:
```bash
# Development (with rebuild)
npm run dev

# Production
npm start

# Stop services
npm stop

# Clean up (remove containers and images)
npm run clean
```

## 📁 Project Structure

```
adobe-hackathon-backend/
├── README.md
├── package.json
├── docker-compose.yml
│
├── nestjs-backend/
│   ├── src/
│   │   ├── main.ts                          # Application entry point
│   │   ├── app.module.ts                    # Root module
│   │   ├── app.controller.ts                # Health check endpoints
│   │   ├── app.service.ts                   # Basic app services
│   │   └── pdf-extraction/
│   │       ├── pdf-extraction.module.ts     # PDF extraction module
│   │       ├── pdf-extraction.controller.ts # File upload endpoint
│   │       ├── pdf-extraction.service.ts    # Python service integration
│   │       └── dto/
│   │           └── document-structure.dto.ts # Response DTOs
│   ├── package.json
│   ├── tsconfig.json
│   ├── nest-cli.json
│   └── Dockerfile
│
└── python-parser/
    ├── src/
    │   ├── main.py                          # FastAPI application
    │   ├── pdf_parser.py                    # PyMuPDF text extraction
    │   └── heading_classifier.py            # Heading classification logic
    ├── requirements.txt
    └── Dockerfile
```

## ✅ Features Implemented

### Core Requirements ✅
- [x] PDF upload endpoint (≤ 50 pages)
- [x] Document title extraction
- [x] H1, H2, H3 heading detection with page numbers
- [x] JSON response format
- [x] NestJS + Python microservice architecture
- [x] Docker containerization

### Bonus Features ✅
- [x] Font metrics caching and analysis
- [x] Comprehensive error handling and logging
- [x] API documentation with Swagger
- [x] Health check endpoints
- [x] Processing time metrics
- [x] Robust pattern-based classification
- [x] Multi-language font support
- [x] Performance optimizations

## 🔧 Configuration

### Environment Variables:
- `NODE_ENV`: Node.js environment (development/production)
- `PORT`: NestJS server port (default: 3000)
- `PYTHON_SERVICE_URL`: Python service URL (default: http://python-parser:8000)
- `LOG_LEVEL`: Python logging level (default: INFO)

### Customization:
- PDF size limits: Modify validation in `pdf-extraction.controller.ts`
- Heading classification: Adjust heuristics in `heading_classifier.py`
- Font thresholds: Update percentiles in `_calculate_font_thresholds()`

## 🐛 Troubleshooting

### Common Issues:

1. **Services not starting**:
   ```bash
   docker-compose logs
   docker-compose down && docker-compose up --build
   ```

2. **Python service connection failed**:
   - Ensure both services are in the same Docker network
   - Check Python service health: http://localhost:8000/health

3. **PDF processing errors**:
   - Verify PDF is not encrypted or corrupted
   - Check file size ≤ 50MB and ≤ 50 pages
   - Review Python service logs: `docker-compose logs python-parser`

4. **Memory issues**:
   - Increase Docker memory allocation to 4GB+
   - Monitor resource usage: `docker stats`

### Logs:
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f nestjs-backend
docker-compose logs -f python-parser
```

## 🎯 Adobe Hackathon Context

This implementation addresses **Round 1A: Document Structure Extraction** requirements:

- ✅ Extracts structural outline from PDFs (≤ 50 pages)
- ✅ Returns JSON with document title and H1/H2/H3 headings
- ✅ Includes page numbers for each heading
- ✅ Uses advanced NLP and layout analysis techniques
- ✅ Containerized for easy deployment and evaluation
- ✅ Provides comprehensive API documentation
- ✅ Implements robust error handling and logging

**Ready for Adobe evaluation! 🚀**

---

*Built with ❤️ for Adobe India Hackathon - Connecting the Dots* 