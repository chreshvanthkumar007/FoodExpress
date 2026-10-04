@echo off
title FoodExpress Launcher
cd /d "%~dp0"

echo ==========================================================
echo          FoodExpress - Online Food Delivery System
echo ==========================================================
echo.
echo   [1] Start Local Server (http://127.0.0.1:5000) [Default]
echo   [2] Start Local Server + Public Cloudflare Tunnel
echo   [3] Initialize / Verify Database (MySQL / SQLite)
echo   [4] Run Automated Test Suite (13 Tests)
echo   [5] Exit
echo.
echo ==========================================================
set /p choice="Enter choice [1-5] (Press Enter for Option 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto start_local
if "%choice%"=="2" goto start_public
if "%choice%"=="3" goto init_db
if "%choice%"=="4" goto run_tests
if "%choice%"=="5" goto end

:start_local
call "%~dp0start_server.bat"
goto end

:start_public
call "%~dp0start_public.bat"
goto end

:init_db
python "%~dp0init_db.py"
pause
goto end

:run_tests
python "%~dp0test_app.py"
pause
goto end

:end
