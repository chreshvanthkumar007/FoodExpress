@echo off
title FoodExpress Public Cloudflare Tunnel
echo ========================================================
echo   FoodExpress: Launching Worldwide Public HTTPS Tunnel
echo ========================================================
echo.
echo Starting tunnel to local port 5000...
echo Share the generated https://*.trycloudflare.com link with anyone!
echo.
set CLOUDFLARED_CMD=cloudflared
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    set CLOUDFLARED_CMD="C:\Program Files (x86)\cloudflared\cloudflared.exe"
) else if exist "C:\Program Files\cloudflared\cloudflared.exe" (
    set CLOUDFLARED_CMD="C:\Program Files\cloudflared\cloudflared.exe"
)

%CLOUDFLARED_CMD% tunnel --url http://127.0.0.1:5000
pause
