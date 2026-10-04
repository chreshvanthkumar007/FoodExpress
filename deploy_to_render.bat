@echo off
title FoodExpress - Deploy to Render (Cloud Hosting)
echo ========================================================
echo   FoodExpress: Push Code to GitHub for Render Deployment
echo ========================================================
cd /d "%~dp0"

echo.
echo [*] Checking Git repository status...
git status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Initializing Git repository...
    git init
    git branch -M main
    git add .
    git commit -m "Initial commit for Render deployment"
)

echo.
echo ========================================================
echo   STEP 1: Create a GitHub Repository
echo ========================================================
echo   1. Open: https://github.com/new
echo   2. Repository Name: FoodExpress
echo   3. Set to: Public (or Private)
echo   4. Do NOT initialize with README/license
echo   5. Click "Create repository"
echo ========================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/YOUR_USERNAME/FoodExpress.git): "

if "%REPO_URL%"=="" (
    echo [!] No URL entered. Aborting push.
    pause
    exit /b 1
)

echo.
echo [*] Linking remote origin...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo [*] Pushing main branch to GitHub...
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Push failed. Please check your GitHub permissions / credentials.
    echo [*] If GitHub asks to authenticate, log in via your browser or Personal Access Token.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   [SUCCESS] Code pushed to GitHub!
echo ========================================================
echo.
echo [*] Now launching Render in your default browser...
start https://dashboard.render.com/select-repo?type=web
echo.
echo ========================================================
echo   FINAL STEP ON RENDER:
echo   1. Sign in with GitHub on dashboard.render.com
echo   2. Select your 'FoodExpress' repository
echo   3. Render detects 'render.yaml' automatically!
echo   4. Click 'Apply' / 'Create Web Service'
echo.
echo   Your 24/7 permanent link will be generated in 2 minutes:
echo   👉 https://foodexpress-xxxx.onrender.com
echo ========================================================
echo.
pause
