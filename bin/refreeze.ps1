# PowerShell script to rebuild container and freeze dependencies
# Equivalent to refreeze.sh for Windows

$ErrorActionPreference = "Stop"

Write-Host "Copying requirements.top to requirements.txt..."
Copy-Item requirements.top requirements.txt

Write-Host "Building pdf-agent container..."
docker-compose build pdf-agent

Write-Host "Freezing dependencies..."
docker-compose run --rm --no-deps pdf-agent sh -c 'pip freeze > requirements.txt'

Write-Host "Processing GitHub URLs..."
$githubUrls = Select-String -Path requirements.top -Pattern '^[^#].*egg=(.*)' | ForEach-Object {
    if ($_.Matches[0].Groups[1].Value) {
        $packageName = $_.Matches[0].Groups[1].Value
        $fullLine = $_.Line
        "s%$packageName=.*%$fullLine%"
    }
}

if ($githubUrls) {
    $tempFile = [System.IO.Path]::GetTempFileName()
    $githubUrls | Set-Content $tempFile
    
    $content = Get-Content requirements.txt
    foreach ($pattern in $githubUrls) {
        if ($pattern -match 's%(.*)=.*%(.*)%') {
            $packageName = $matches[1]
            $replacement = $matches[2]
            $content = $content -replace "$packageName=.*", $replacement
        }
    }
    $content | Set-Content requirements.new
    Remove-Item $tempFile
}
else {
    Copy-Item requirements.txt requirements.new
}

Move-Item requirements.new requirements.txt -Force

Write-Host "Dependencies frozen successfully!"
