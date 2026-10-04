@echo off
title Push FoodExpress to GitHub
echo ========================================================
echo   Pushing FoodExpress to GitHub
echo   Target: https://github.com/chreshvanthkumar007/FoodExpress.git
echo ========================================================
echo.
cd /d "%~dp0"
git remote set-url origin https://github.com/chreshvanthkumar007/FoodExpress.git
echo [*] Pushing main branch to GitHub...
echo [*] If a GitHub Sign-in window appears, click "Sign in with your browser".
echo.
git push -u origin main --force
echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo   [SUCCESS] Code successfully pushed to GitHub!
    echo   Repository: https://github.com/chreshvanthkumar007/FoodExpress
    echo ========================================================
) else (
    echo.
    echo [!] Push could not be completed. Please check your GitHub login.
)
echo.
pause
