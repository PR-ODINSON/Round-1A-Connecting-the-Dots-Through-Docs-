#!/bin/bash
# Adobe India Hackathon 2025 - Round 1A API Test Script
# Document Structure Extraction Demo

echo "🎯 Adobe India Hackathon 2025 - Round 1A Demo"
echo "=============================================="
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if services are running
echo -e "${BLUE}1. Checking Service Health...${NC}"
echo "----------------------------------------"

# Check NestJS API
echo -n "🔍 NestJS API (Port 3000): "
if curl -s http://localhost:3000/health > /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not Running${NC}"
    echo "Please start services with: docker-compose up --build -d"
    exit 1
fi

# Check Python Service
echo -n "🐍 Python Service (Port 8000): "
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not Running${NC}"
    exit 1
fi

echo

# Test PDF Processing
echo -e "${BLUE}2. Testing PDF Document Structure Extraction...${NC}"
echo "------------------------------------------------"

# Check if sample PDF exists
if [ ! -f "python-parser/sample.pdf" ]; then
    echo -e "${RED}❌ Sample PDF not found: python-parser/sample.pdf${NC}"
    exit 1
fi

echo "📄 Processing: python-parser/sample.pdf"
echo "⏱️  Processing..."

# Make API call and capture response
RESPONSE=$(curl -s -X POST \
  http://localhost:3000/pdf-extraction/parse-pdf \
  -H "Content-Type: multipart/form-data" \
  -F "file=@python-parser/sample.pdf")

# Check if response is valid JSON
if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PDF processed successfully!${NC}"
    echo
    
    # Extract key information
    TITLE=$(echo "$RESPONSE" | jq -r '.title')
    OUTLINE_COUNT=$(echo "$RESPONSE" | jq '.outline | length')
    TOTAL_PAGES=$(echo "$RESPONSE" | jq -r '.metadata.totalPages')
    PROCESSING_TIME=$(echo "$RESPONSE" | jq -r '.metadata.processingTimeMs')
    
    echo -e "${BLUE}3. Adobe Schema Output Results:${NC}"
    echo "-------------------------------"
    echo "📖 Document Title: $TITLE"
    echo "📋 Outline Items: $OUTLINE_COUNT headings"
    echo "📄 Total Pages: $TOTAL_PAGES"
    echo "⚡ Processing Time: ${PROCESSING_TIME}ms"
    echo
    
    # Show first few outline items
    echo -e "${BLUE}4. Sample Outline Structure:${NC}"
    echo "-----------------------------"
    echo "$RESPONSE" | jq -r '.outline[0:3][] | "• \(.level): \(.text) (Page \(.page))"'
    echo
    
    # Show formatted JSON response
    echo -e "${BLUE}5. Complete Adobe Schema Response:${NC}"
    echo "-----------------------------------"
    echo "$RESPONSE" | jq .
    
else
    echo -e "${RED}❌ Error processing PDF:${NC}"
    echo "$RESPONSE"
    exit 1
fi

echo
echo -e "${GREEN}🎊 Adobe India Hackathon 2025 - Round 1A Demo Complete!${NC}"
echo -e "${YELLOW}📖 API Documentation: http://localhost:3000/api${NC}"
echo -e "${YELLOW}🐍 Python Docs: http://localhost:8000/docs${NC}"
echo
echo -e "${GREEN}✅ Ready for Adobe Evaluation!${NC}" 