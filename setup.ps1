# Setup script for Windows PowerShell

Write-Host "🚀 Setting up PDF Q&A Agent..." -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env and add your OPENAI_API_KEY" -ForegroundColor Yellow
    exit 1
}

# Check if OpenAI key is set
$envContent = Get-Content .env -Raw
if ($envContent -match "your-openai-api-key-here") {
    Write-Host "⚠️  Please add your OPENAI_API_KEY to .env file" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
try {
    docker ps | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites checked" -ForegroundColor Green
Write-Host "🔨 Building Docker image..." -ForegroundColor Cyan

docker-compose build pdf-agent

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 To start the service, run:" -ForegroundColor Cyan
    Write-Host "   docker-compose up pdf-agent" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 Or run in background:" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d pdf-agent" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 Then visit: http://localhost:8200/docs" -ForegroundColor Cyan
} else {
    Write-Host "❌ Build failed. Check the error messages above." -ForegroundColor Red
    exit 1
}
