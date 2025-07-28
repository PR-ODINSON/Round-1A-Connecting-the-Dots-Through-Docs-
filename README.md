# Adobe India Hackathon 2025 - Round 1A: Document Structure Extraction

🎯 **Official Submission** for Adobe India Hackathon 2025 - "Connecting the Dots"

**Challenge:** Round 1A - Document Structure Extraction from PDF Files (≤ 50 pages)

## 🏆 **Dual Architecture Solution**

This submission provides **two implementation approaches** to meet different evaluation criteria:

### 🐳 **Challenge 1A Containerized Solution** (Primary Submission)
**✅ MEETS ALL OFFICIAL REQUIREMENTS**
- **Single Docker Container**: Processes PDFs from `/app/input` to `/app/output`
- **No Network Access**: All models bundled in container
- **≤ 10 seconds**: Optimized for 50-page PDF processing
- **≤ 200MB**: Lightweight model constraints
- **AMD64 Compatible**: Cross-platform deployment
- **Exact Schema**: Matches `output_schema.json`

```bash
# Official Challenge 1A Commands
docker build --platform linux/amd64 -t adobe-pdf-processor .
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-pdf-processor
```

### 🏗️ **Microservice Architecture** (Comprehensive Solution)
Advanced NestJS + Python FastAPI architecture with:
- **Production-grade API**: REST endpoints with Swagger docs
- **Advanced AI Classification**: spaCy + NLTK + sophisticated heuristics
- **Health Monitoring**: Service health checks and logging
- **Comprehensive Testing**: API validation and error handling

## 🎯 Challenge 1A Compliance

### ✅ **Official Requirements Met**
- [x] **Dockerfile**: Present in root directory and functional
- [x] **Build Command**: `docker build --platform linux/amd64 -t <name> .`
- [x] **Run Command**: `docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none <name>`
- [x] **Execution Time**: ≤ 10 seconds for 50-page PDFs
- [x] **Model Size**: ≤ 200MB (optimized spaCy + PyMuPDF)
- [x] **No Network**: Offline processing with bundled models
- [x] **AMD64 Architecture**: Cross-platform compatibility
- [x] **Automatic Processing**: Processes all PDFs from input directory
- [x] **Schema Compliance**: Exact match with `output_schema.json`

### 📊 **Performance Optimizations**
- **Fast PDF Processing**: Optimized PyMuPDF extraction
- **Efficient Font Analysis**: Percentile-based thresholds
- **Smart Pattern Recognition**: High-priority heading patterns
- **Memory Management**: Minimal memory footprint
- **CPU Optimization**: Efficient use of available cores

---

## 🏆 Team Information

- **Team Name:** Adobe Document Intelligence Team
- **Challenge:** Round 1A - Document Structure Extraction
- **Submission Date:** January 26, 2025
- **Technology Stack:** Python + PyMuPDF + spaCy + NLTK (Challenge 1A) | NestJS + FastAPI (Microservice)

## 📋 Problem Statement

Build a backend system that extracts structured outlines from PDF documents and returns them in JSON format, including:
- **Document Title** (extracted intelligently from content)
- **Hierarchical Headings** (H1, H2, H3) with page numbers
- **Font Analytics** and processing metadata
- **Adobe's Official Schema** (`outline` field with `level` properties)

### 🎯 Requirements Met
✅ **PDF Processing**: Up to 50 pages, 50MB max size  
✅ **JSON Output**: Adobe's official schema format  
✅ **Heading Detection**: Advanced NLP + heuristic classification  
✅ **Title Extraction**: Intelligent document title identification  
✅ **Containerized**: Single Docker container solution  
✅ **Performance**: Sub-10-second processing  
✅ **Offline**: No network access required  
✅ **Cross-Platform**: AMD64 architecture support  

---

## 🚀 Quick Start - Challenge 1A

### Prerequisites
- Docker with AMD64 support
- Input PDFs in `./input` directory

### 1. Build Container
```bash
# Official Challenge 1A build command
docker build --platform linux/amd64 -t adobe-pdf-processor .
```

### 2. Prepare Test Data
```bash
# Create input and output directories
mkdir -p input output

# Copy your PDF files to input directory
cp your-pdfs/*.pdf input/
```

### 3. Run Processing
```bash
# Official Challenge 1A run command
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  adobe-pdf-processor
```

### 4. Check Results
```bash
# View generated JSON files
ls output/
cat output/your-file.json
```

---

## 🏗️ Alternative: Microservice Architecture

For development and advanced features, use the full microservice architecture:

```bash
# Start microservices
docker-compose up --build -d

# Test API
curl -X POST http://localhost:3000/pdf-extraction/parse-pdf \
  -F "file=@sample.pdf"

# View API docs
open http://localhost:3000/api
```

---

## 📤 Adobe Official Schema Output

Both solutions return data in **Adobe's exact schema format**:

```json
{
  "title": "AI in Healthcare: A Comprehensive Review",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Problem Statement",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Scope and Limitations", 
      "page": 3
    }
  ]
}
```

---

## 🧠 AI-Powered Heading Classification

Our advanced classification system uses multiple approaches:

### 1. **Font Analysis**
- Percentile-based size thresholds (top 5%, 15%, 30%)
- Bold/italic style detection
- Font family analysis

### 2. **Pattern Recognition**
- Chapter patterns: `"Chapter 1"`, `"1. Introduction"`
- Numbered sections: `"1.1 Overview"`, `"1.1.1 Details"`
- Common keywords: `"Introduction"`, `"Summary"`, `"Conclusion"`

### 3. **Performance Optimizations**
- **Fast PDF parsing**: Optimized PyMuPDF extraction
- **Efficient text analysis**: Priority-based pattern matching
- **Memory optimization**: Minimal footprint for large documents
- **CPU efficiency**: Parallel processing where applicable

---

## 📁 Project Structure (Challenge 1A)

```
adobe-hackathon-backend/
├── Dockerfile                     # Main Challenge 1A container
├── requirements.txt               # Optimized dependencies
├── process_pdfs.py                # Main processing script
├── pdf_processor.py               # AI classification engine
│
├── input/                         # PDF input directory (mount point)
├── output/                        # JSON output directory (mount point)
│
├── nestjs-backend/                # Microservice architecture (optional)
├── python-parser/                 # FastAPI service (optional)
├── docker-compose.yml             # Multi-service deployment (optional)
└── README.md                      # This comprehensive guide
```

---

## ✅ Challenge 1A Validation

### Required Constraints ✅
- [x] **10-second limit**: Optimized processing pipeline
- [x] **200MB model**: Lightweight spaCy + efficient dependencies
- [x] **No network**: All models bundled in container
- [x] **AMD64**: Cross-platform Docker build
- [x] **Schema compliance**: Exact JSON output format
- [x] **Automatic processing**: Handles all input PDFs
- [x] **Error handling**: Graceful failure with valid output

### Testing Commands
```bash
# Build and test locally
docker build --platform linux/amd64 -t test-processor .

# Test with sample data
docker run --rm \
  -v $(pwd)/test-input:/app/input:ro \
  -v $(pwd)/test-output:/app/output \
  --network none \
  test-processor

# Validate output schema
python -c "import json; print(json.load(open('test-output/sample.json')))"
```

### Performance Validation
- **Processing Time**: Measured and logged for each PDF
- **Memory Usage**: Optimized for 16GB constraint
- **CPU Utilization**: Efficient use of 8 available cores
- **File Size**: Container size ≤ 200MB requirement

---

## 🎯 Adobe Hackathon Context

This implementation specifically addresses **Adobe India Hackathon 2025 - Round 1A** requirements:

### ✅ **Challenge 1A Compliance**
- **Single Container Solution** ✅
- **Offline Processing** (no network) ✅
- **Performance Constraints** (≤10s, ≤200MB) ✅
- **Exact Schema Output** ✅
- **AMD64 Architecture** ✅
- **Automatic Processing** ✅

### 🚀 **Competitive Advantages**
1. **Dual Architecture**: Challenge 1A + Microservice solutions
2. **Advanced AI**: Multi-modal classification with NLP
3. **Performance Optimized**: Sub-10-second processing
4. **Production Ready**: Enterprise-grade error handling
5. **Schema Compliant**: Exact Adobe format matching
6. **Cross-Platform**: AMD64 and development support

---

## 🧪 Testing & Validation

### 1. **Challenge 1A Testing**
```bash
# Quick validation
./test-challenge-1a.sh

# Manual testing
docker build --platform linux/amd64 -t adobe-processor .
docker run --rm -v $(pwd)/input:/app/input:ro -v $(pwd)/output:/app/output --network none adobe-processor
```

### 2. **Performance Testing**
```bash
# Time large PDF processing
time docker run --rm -v $(pwd)/large-pdfs:/app/input:ro -v $(pwd)/results:/app/output --network none adobe-processor
```

### 3. **Schema Validation**
```bash
# Validate output format
python -m jsonschema -i output/file.json schema/output_schema.json
```

---

## 🎊 **Ready for Adobe Evaluation!**

This **Document Structure Extraction** solution is fully ready for Adobe India Hackathon 2025 submission:

### **Challenge 1A Submission** ✅
- ✅ **Complete Implementation** of all requirements
- ✅ **Performance Optimized** for ≤10s processing
- ✅ **Container Ready** with official build/run commands
- ✅ **Schema Compliant** with exact output format
- ✅ **Offline Processing** with bundled models
- ✅ **Cross-Platform** AMD64 support

### **Bonus: Microservice Architecture** ✅
- ✅ **Production API** with comprehensive documentation
- ✅ **Advanced AI** with sophisticated classification
- ✅ **Health Monitoring** and enterprise features
- ✅ **Comprehensive Testing** and validation

**🚀 Build. Test. Submit. Win!**

---

*Built with ❤️ for Adobe India Hackathon 2025 - "Connecting the Dots"*