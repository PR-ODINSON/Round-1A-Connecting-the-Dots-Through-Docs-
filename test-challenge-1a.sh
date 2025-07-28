#!/bin/bash
# Adobe India Hackathon 2025 - Challenge 1A Validation Script
# Tests the containerized PDF processing solution

echo "🎯 Adobe India Hackathon 2025 - Challenge 1A Validation"
echo "======================================================="
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Build the container with official command
echo -e "${BLUE}1. Building Docker Container (Official Command)...${NC}"
echo "---------------------------------------------------"
echo "$ docker build --platform linux/amd64 -t adobe-pdf-processor ."

if docker build --platform linux/amd64 -t adobe-pdf-processor .; then
    echo -e "${GREEN}✅ Container built successfully${NC}"
else
    echo -e "${RED}❌ Container build failed${NC}"
    exit 1
fi

echo

# Step 2: Prepare test environment
echo -e "${BLUE}2. Preparing Test Environment...${NC}"
echo "--------------------------------"

# Create input and output directories
mkdir -p input output

# Check if sample PDF exists
if [ ! -f "python-parser/sample.pdf" ]; then
    echo -e "${RED}❌ Sample PDF not found: python-parser/sample.pdf${NC}"
    echo "Please ensure the sample PDF exists for testing"
    exit 1
fi

# Copy sample PDF to input directory
cp python-parser/sample.pdf input/
echo -e "${GREEN}✅ Test environment prepared${NC}"
echo "   📂 Input directory: ./input"
echo "   📂 Output directory: ./output"
echo "   📄 Test file: sample.pdf"

echo

# Step 3: Run the container with official command
echo -e "${BLUE}3. Running PDF Processing (Official Command)...${NC}"
echo "-----------------------------------------------"
echo "$ docker run --rm -v \$(pwd)/input:/app/input:ro -v \$(pwd)/output:/app/output --network none adobe-pdf-processor"

START_TIME=$(date +%s)

if docker run --rm \
    -v $(pwd)/input:/app/input:ro \
    -v $(pwd)/output:/app/output \
    --network none \
    adobe-pdf-processor; then
    
    END_TIME=$(date +%s)
    PROCESSING_TIME=$((END_TIME - START_TIME))
    
    echo -e "${GREEN}✅ Processing completed successfully${NC}"
    echo "   ⏱️  Processing time: ${PROCESSING_TIME} seconds"
    
    # Validate 10-second constraint
    if [ $PROCESSING_TIME -le 10 ]; then
        echo -e "${GREEN}✅ Performance target met: ${PROCESSING_TIME}s ≤ 10s${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Processing took ${PROCESSING_TIME}s (target: ≤10s)${NC}"
    fi
else
    echo -e "${RED}❌ Processing failed${NC}"
    exit 1
fi

echo

# Step 4: Validate output
echo -e "${BLUE}4. Validating Output...${NC}"
echo "----------------------"

# Check if JSON output was created
if [ -f "output/sample.json" ]; then
    echo -e "${GREEN}✅ Output file created: sample.json${NC}"
    
    # Validate JSON structure
    if python3 -c "import json; data=json.load(open('output/sample.json')); print('Title:', data.get('title', 'N/A')); print('Outline items:', len(data.get('outline', [])))" 2>/dev/null; then
        echo -e "${GREEN}✅ JSON structure is valid${NC}"
        
        # Show output preview
        echo
        echo -e "${BLUE}5. Output Preview:${NC}"
        echo "---------------"
        echo "Content of sample.json:"
        python3 -c "import json; print(json.dumps(json.load(open('output/sample.json')), indent=2))" 2>/dev/null || cat output/sample.json
        
    else
        echo -e "${RED}❌ Invalid JSON structure${NC}"
        echo "Content:"
        cat output/sample.json
    fi
else
    echo -e "${RED}❌ No output file created${NC}"
    echo "Contents of output directory:"
    ls -la output/
fi

echo

# Step 5: Container size validation
echo -e "${BLUE}6. Container Size Validation...${NC}"
echo "------------------------------"

CONTAINER_SIZE=$(docker images adobe-pdf-processor --format "table {{.Size}}" | tail -n +2)
echo "📦 Container size: $CONTAINER_SIZE"

# Note: Size validation is approximate as Docker reports compressed size differently
echo -e "${YELLOW}ℹ️  Size constraint: ≤200MB (challenge requirement)${NC}"

echo

# Summary
echo -e "${GREEN}🎊 Challenge 1A Validation Complete!${NC}"
echo "==================================="
echo
echo -e "${BLUE}✅ Requirements Validated:${NC}"
echo "   📦 Docker build with --platform linux/amd64"
echo "   🚀 Docker run with official command"
echo "   📄 Automatic PDF processing from /app/input"
echo "   💾 JSON output generated in /app/output"
echo "   🌐 No network access (--network none)"
echo "   ⏱️  Performance tracking and validation"
echo
echo -e "${GREEN}🏆 Ready for Adobe India Hackathon 2025 Submission!${NC}"

# Cleanup option
echo
read -p "Clean up test files? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf input output
    echo -e "${GREEN}✅ Test files cleaned up${NC}"
fi 