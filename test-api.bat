@echo off
echo.
echo 🧪 Adobe Hackathon - API Testing Script
echo ========================================

set NESTJS_URL=http://localhost:3000
set PYTHON_URL=http://localhost:8000

echo.
echo 🏥 Health Checks
echo ----------------

echo 📡 Checking NestJS Backend...
curl -s -f "%NESTJS_URL%/health" >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ NestJS Backend Running
) else (
    echo ✗ NestJS Backend Not accessible
    goto :error
)

echo 📡 Checking Python Parser...
curl -s -f "%PYTHON_URL%/health" >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Python Parser Running
) else (
    echo ✗ Python Parser Not accessible
    goto :error
)

echo.
echo 🧪 API Endpoint Tests
echo ---------------------

echo 🔍 Testing NestJS root endpoint...
curl -s "%NESTJS_URL%" >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ NestJS root endpoint OK
) else (
    echo ✗ NestJS root endpoint Failed
)

echo 🔍 Testing Python root endpoint...
curl -s "%PYTHON_URL%" >nul 2>&1
if %errorlevel% == 0 (
    echo ✓ Python root endpoint OK
) else (
    echo ✗ Python root endpoint Failed
)

echo.
echo 📖 Documentation Links
echo ----------------------
echo • NestJS API Docs: %NESTJS_URL%/api
echo • Python API Docs: %PYTHON_URL%/docs
echo.

echo 🎯 PDF Upload Test
echo ------------------
echo To test PDF upload, run:
echo curl -X POST %NESTJS_URL%/pdf-extraction/parse-pdf -H "Content-Type: multipart/form-data" -F "file=@your-document.pdf"
echo.

echo ✅ All basic tests completed!
echo.
echo 🚀 Ready for Adobe Hackathon evaluation!
goto :end

:error
echo.
echo ⚠️  Some services are not running. Please start with:
echo    docker-compose up --build
echo.

:end
pause 