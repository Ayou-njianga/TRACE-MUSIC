# Start all services (cloudrpc, AuthService, backend) in separate PowerShell windows
# Usage: Open PowerShell as Administrator (if needed), then run: .\start_all.ps1
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "Starting CloudRPC server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location -Path \"$root\cloudrpc\"; ./start_cloudrpc.ps1"

Start-Sleep -Milliseconds 500
Write-Host "Starting AuthService..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location -Path \"$root\AuthService\"; ./start_authservice.ps1"

Start-Sleep -Milliseconds 500
Write-Host "Starting Backend (REST API)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit","-Command","Set-Location -Path \"$root\backend\"; ./start_backend.ps1"

Write-Host "All services launched. Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

# Open client portal in default browser
$clientUrl = "http://127.0.0.1:8000/client/"
Write-Host "Opening client portal: $clientUrl" -ForegroundColor Cyan
Start-Process $clientUrl

Write-Host "If any service fails to start, check the individual start scripts in each folder." -ForegroundColor Magenta
