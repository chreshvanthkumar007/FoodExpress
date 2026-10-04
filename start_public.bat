@echo off
title FoodExpress - Start Server & Public Tunnel
echo ========================================================
echo   FoodExpress: Starting Server + Public Access Tunnel
echo ========================================================
cd /d "%~dp0"

echo.
echo [*] Local Network (Wi-Fi) Access:
powershell.exe -NoProfile -Command "$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback|vEthernet' -and $_.IPAddress -notlike '169.254*' } | Select-Object -ExpandProperty IPAddress -First 1); Write-Host '    -> Local LAN / Wi-Fi URL: http://' $ip ':5000' -ForegroundColor Green"
echo.
echo [*] Launching FoodExpress Server in a separate window...
start "FoodExpress Server Console" "%~dp0start_server.bat"

echo.
echo [*] Launching Cloudflare Tunnel for Worldwide Public Access...
echo [*] A public URL like https://xxxxxxxx.trycloudflare.com will appear below:
echo [*] Share that HTTPS link with anyone on the internet to let them access FoodExpress!
echo ========================================================
echo.

set CLOUDFLARED_CMD=cloudflared
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    set CLOUDFLARED_CMD="C:\Program Files (x86)\cloudflared\cloudflared.exe"
) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
    set CLOUDFLARED_CMD="C:\Program Files\cloudflared\cloudflared.exe"
)

%CLOUDFLARED_CMD% tunnel --url http://127.0.0.1:5000
pause
