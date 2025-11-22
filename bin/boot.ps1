# PowerShell script for Windows

$ErrorActionPreference = "Stop"

$BinRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Wait for database to be ready
$maxAttempts = 15
$attempt = 0
$dbReady = $false

Write-Host "Waiting for database at ${env:DB_HOST}:${env:DB_PORT}..."

while (-not $dbReady -and $attempt -lt $maxAttempts) {
    $attempt++
    try {
        $connection = New-Object System.Net.Sockets.TcpClient($env:DB_HOST, $env:DB_PORT)
        $connection.Close()
        $dbReady = $true
        Write-Host "Database is ready!"
    }
    catch {
        Write-Host "Attempt $attempt/$maxAttempts - Database not ready yet..."
        Start-Sleep -Seconds 1
    }
}

if (-not $dbReady) {
    Write-Host "Database did not become ready in time"
    exit 1
}

# Run alembic migrations
alembic upgrade head

# Start the application
if ($env:ENVIRONMENT -eq "development") {
    uvicorn --reload --workers 1 --host 0.0.0.0 --port 80 pdf_agent.app:app
}
else {
    python -m gunicorn --config=gunicorn_conf.py pdf_agent.app:app
}
