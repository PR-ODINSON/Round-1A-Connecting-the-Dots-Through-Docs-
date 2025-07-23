#!/bin/bash

echo "🧪 Adobe Hackathon - API Testing Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URLs
NESTJS_URL="http://localhost:3000"
PYTHON_URL="http://localhost:8000"

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    
    echo -n "📡 Checking $service_name... "
    if curl -s -f "$url/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not accessible${NC}"
        return 1
    fi
}

# Function to test endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local description=$3
    
    echo -n "🔍 Testing $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "$url" -o /tmp/response.json)
    else
        response=$(curl -s -w "%{http_code}" -X "$method" "$url" -o /tmp/response.json)
    fi
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed (HTTP $response)${NC}"
        return 1
    fi
}

echo ""
echo "🏥 Health Checks"
echo "----------------"

# Check services
check_service "$NESTJS_URL" "NestJS Backend"
nestjs_status=$?

check_service "$PYTHON_URL" "Python Parser"
python_status=$?

if [ $nestjs_status -ne 0 ] || [ $python_status -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some services are not running. Please start with:${NC}"
    echo "   docker-compose up --build"
    echo ""
    exit 1
fi

echo ""
echo "🧪 API Endpoint Tests"
echo "---------------------"

# Test endpoints
test_endpoint "GET" "$NESTJS_URL" "NestJS root endpoint"
test_endpoint "GET" "$NESTJS_URL/health" "NestJS health check"
test_endpoint "GET" "$PYTHON_URL" "Python root endpoint"
test_endpoint "GET" "$PYTHON_URL/health" "Python health check"

echo ""
echo "📖 Documentation Links"
echo "----------------------"
echo "• NestJS API Docs: $NESTJS_URL/api"
echo "• Python API Docs: $PYTHON_URL/docs"
echo ""

echo "🎯 PDF Upload Test"
echo "------------------"
echo "To test PDF upload, run:"
echo "curl -X POST \\"
echo "  $NESTJS_URL/pdf-extraction/parse-pdf \\"
echo "  -H \"Content-Type: multipart/form-data\" \\"
echo "  -F \"file=@your-document.pdf\""
echo ""

echo -e "${GREEN}✅ All basic tests completed!${NC}"
echo ""
echo "🚀 Ready for Adobe Hackathon evaluation!" 