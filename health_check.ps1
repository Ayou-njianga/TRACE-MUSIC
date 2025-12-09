# CloudSim Health Check - Validates system before startup
# Checks for all required files, dependencies, and configuration

Write-Host "CloudSim Health Check" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$issues = @()
$warnings = @()
$success = @()

# Check required directories
Write-Host "Checking directory structure..." -ForegroundColor Yellow
$dirs = @(
    "CloudSim",
    "backend",
    "cloudrpc",
    "AuthService",
    "frontend/apps/client/public",
    "frontend/apps/provider/public"
)

foreach ($dir in $dirs) {
    $path = Join-Path $root $dir
    if (Test-Path -Path $path -PathType Container) {
        $success += "✓ Directory exists: $dir"
    } else {
        $issues += "✗ Missing directory: $dir"
    }
}

# Check required files
Write-Host "Checking required files..." -ForegroundColor Yellow
$files = @(
    "backend/api.py",
    "backend/start_backend.ps1",
    "cloudrpc/server.py",
    "cloudrpc/start_cloudrpc.ps1",
    "AuthService/cloud.py",
    "AuthService/start_authservice.ps1",
    "frontend/apps/client/public/index.html",
    "frontend/apps/client/public/main.js",
    "frontend/apps/provider/public/index.html",
    "frontend/apps/provider/public/main.js",
    "CloudSim/config.yaml",
    "CloudSim/main.py"
)

foreach ($file in $files) {
    $path = Join-Path $root $file
    if (Test-Path -Path $path -PathType Leaf) {
        $success += "✓ File exists: $file"
    } else {
        $issues += "✗ Missing file: $file"
    }
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = & python --version 2>&1
    $success += "✓ Python installed: $pythonVersion"
} else {
    $issues += "✗ Python not found in PATH"
}

# Check required Python packages
Write-Host "Checking Python packages..." -ForegroundColor Yellow
$packages = @("fastapi", "uvicorn", "pydantic", "grpcio", "pyyaml")
foreach ($pkg in $packages) {
    try {
        $result = & python -c "import $($pkg.Replace('-', '_')); print('OK')" 2>&1
        if ($result -eq "OK") {
            $success += "✓ Package installed: $pkg"
        } else {
            $warnings += "⚠ Package may not be installed correctly: $pkg"
        }
    } catch {
        $warnings += "⚠ Package not verified: $pkg (may need: pip install $pkg)"
    }
}

# Check port availability
Write-Host "Checking port availability..." -ForegroundColor Yellow
$ports = @(
    @{"port" = 8000; "name" = "Backend API"},
    @{"port" = 50051; "name" = "CloudRPC"},
    @{"port" = 51234; "name" = "AuthService"}
)

foreach ($portInfo in $ports) {
    $port = $portInfo.port
    $name = $portInfo.name
    $tcpConnections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($tcpConnections) {
        $warnings += "⚠ Port $port ($name) already in use - service may fail to start"
    } else {
        $success += "✓ Port $port ($name) available"
    }
}

# Display results
Write-Host ""
Write-Host "Results:" -ForegroundColor Cyan
Write-Host "========" -ForegroundColor Cyan

if ($success.Count -gt 0) {
    Write-Host ""
    $success | ForEach-Object { Write-Host $_ -ForegroundColor Green }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "Warnings:" -ForegroundColor Yellow
    $warnings | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
}

if ($issues.Count -gt 0) {
    Write-Host ""
    Write-Host "Critical Issues:" -ForegroundColor Red
    $issues | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    Write-Host ""
    Write-Host "Fix the issues above before starting the system." -ForegroundColor Red
    Write-Host "Exiting..." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✓ Health check passed! System is ready to start." -ForegroundColor Green
Write-Host ""
Write-Host "Run .\start_all.ps1 to launch all services." -ForegroundColor Cyan
