# FoodExpress - PowerShell Quick Launch Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " FoodExpress - Online Food Delivery System Launch Console" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Robust working directory detection (supports interactive F8 and script execution)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $scriptDir) { $scriptDir = (Get-Location).Path }
Set-Location -LiteralPath $scriptDir

# Auto-detect available Python interpreter
$pythonExe = "python"
if (Test-Path "$scriptDir\.venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\.venv\Scripts\python.exe"
} elseif (Test-Path "$scriptDir\venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\venv\Scripts\python.exe"
} elseif (Test-Path "$scriptDir\..\backend\.venv\Scripts\python.exe") {
    $pythonExe = "$scriptDir\..\backend\.venv\Scripts\python.exe"
} elseif (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pythonExe = "python"
} elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
}

$envFile = Join-Path $scriptDir ".env"
$envExample = Join-Path $scriptDir ".env.example"

if (-not (Test-Path $envFile)) {
    if (Test-Path $envExample) {
        Write-Host "[*] Creating .env file from .env.example..." -ForegroundColor Green
        Copy-Item -LiteralPath $envExample -Destination $envFile
    } else {
        Write-Host "[*] Creating new default .env file..." -ForegroundColor Green
        Set-Content -LiteralPath $envFile -Value "SECRET_KEY=foodexpress_secret_dev_key_2026`nDB_HOST=localhost`nDB_PORT=3306`nDB_USER=root`nDB_PASSWORD=your_mysql_password`nDB_NAME=online_food_delivery" -Encoding utf8
    }
}

# Determine if MySQL root password needs initial configuration
$needsPasswordPrompt = $true
if (Test-Path $envFile) {
    $passLine = Get-Content -LiteralPath $envFile | Where-Object { $_ -match '^DB_PASSWORD=' } | Select-Object -First 1
    if ($passLine -and ($passLine -notmatch '^DB_PASSWORD=your_mysql_password$')) {
        $needsPasswordPrompt = $false
    }
}

# Prompt only if DB_PASSWORD is the unconfigured placeholder or missing
if ($needsPasswordPrompt) {
    Write-Host "[?] Please enter your MySQL 'root' user password (press Enter if blank): " -ForegroundColor Yellow -NoNewline
    $inputPassword = Read-Host
    
    # Update .env with entered password using UTF-8 encoding
    $lines = Get-Content -LiteralPath $envFile
    $updated = $false
    $newContent = [System.Collections.Generic.List[string]]::new()

    foreach ($line in $lines) {
        if ($line -match '^DB_PASSWORD=') {
            $updated = $true
            $newContent.Add("DB_PASSWORD=$inputPassword")
        } else {
            $newContent.Add($line)
        }
    }

    if (-not $updated) {
        $newContent.Add("DB_PASSWORD=$inputPassword")
    }

    $newContent | Set-Content -LiteralPath $envFile -Encoding utf8
    Write-Host "[*] Updated password in .env" -ForegroundColor Green
}

# Run database initializer and start server
Write-Host "[*] Initializing and verifying MySQL database 'online_food_delivery'..." -ForegroundColor Cyan
& $pythonExe init_db.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Database initialization encountered an error (exit code: $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "[!] Please ensure MySQL server is running on port 3306 and credentials in .env are correct." -ForegroundColor Red
}

Write-Host "[*] Starting Flask Application..." -ForegroundColor Green
Write-Host "[*] Access the website at: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "[*] Opening browser in 2 seconds..." -ForegroundColor Cyan

# Launch default browser in the background once server is ready
Start-Job -ScriptBlock { Start-Sleep -Seconds 2; Start-Process "http://127.0.0.1:5000" } | Out-Null

& $pythonExe app.py

