# PowerShell script to test the PDF extraction service

Write-Host "🚀 Testing PDF Structure Extraction Service with PowerShell" -ForegroundColor Green
Write-Host "=" * 60

# Test health check
Write-Host "🔍 Testing health check..." -ForegroundColor Yellow
$healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/" -Method Get
Write-Host "✅ Health check response:" -ForegroundColor Green
$healthResponse | ConvertTo-Json -Depth 3

Write-Host ""

# Test PDF extraction
Write-Host "🔍 Testing PDF extraction..." -ForegroundColor Yellow

# Create form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"sample.pdf`"",
    "Content-Type: application/pdf$LF",
    [System.IO.File]::ReadAllBytes("sample.pdf"),
    "--$boundary--$LF"
) -join $LF

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/extract-headings" -Method Post -Body $bodyLines -ContentType "multipart/form-data; boundary=$boundary"
    Write-Host "✅ PDF extraction successful!" -ForegroundColor Green
    Write-Host "Title: $($response.title)" -ForegroundColor Cyan
    Write-Host "Found $($response.headings.Count) headings:" -ForegroundColor Cyan
    foreach ($heading in $response.headings) {
        Write-Host "  - $($heading.type): $($heading.text) (Page $($heading.page))" -ForegroundColor White
    }
} catch {
    Write-Host "❌ PDF extraction failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Test completed!" -ForegroundColor Green 