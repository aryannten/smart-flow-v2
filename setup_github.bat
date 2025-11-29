@echo off
echo ======================================================================
echo SMART FLOW v2 - GitHub Repository Setup
echo ======================================================================
echo.
echo This script will help you set up your GitHub repository.
echo.
echo BEFORE RUNNING THIS:
echo 1. Create a new repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Have your GitHub username ready
echo.
pause
echo.

set /p GITHUB_URL="Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): "

if "%GITHUB_URL%"=="" (
    echo Error: No URL provided!
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo Step 1: Initializing Git Repository
echo ======================================================================
git init
if errorlevel 1 (
    echo Error: Git initialization failed. Is Git installed?
    pause
    exit /b 1
)
echo ✓ Git initialized

echo.
echo ======================================================================
echo Step 2: Adding Files
echo ======================================================================
git add .
if errorlevel 1 (
    echo Error: Failed to add files
    pause
    exit /b 1
)
echo ✓ Files added

echo.
echo ======================================================================
echo Step 3: Creating Initial Commit
echo ======================================================================
git commit -m "Initial commit: SMART FLOW v2 - AI Traffic Management System"
if errorlevel 1 (
    echo Error: Commit failed
    pause
    exit /b 1
)
echo ✓ Initial commit created

echo.
echo ======================================================================
echo Step 4: Adding Remote Repository
echo ======================================================================
git remote add origin %GITHUB_URL%
if errorlevel 1 (
    echo Warning: Remote might already exist, trying to set URL...
    git remote set-url origin %GITHUB_URL%
)
echo ✓ Remote repository added

echo.
echo ======================================================================
echo Step 5: Pushing to GitHub
echo ======================================================================
echo.
echo You may be prompted for your GitHub credentials.
echo Note: Use a Personal Access Token instead of password if prompted.
echo.
git branch -M main
git push -u origin main

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo Push failed! Common issues:
    echo ======================================================================
    echo 1. Authentication failed
    echo    - Use Personal Access Token instead of password
    echo    - Go to: GitHub Settings → Developer settings → Personal access tokens
    echo.
    echo 2. Repository already has content
    echo    - Try: git pull origin main --allow-unrelated-histories
    echo    - Then: git push -u origin main
    echo.
    echo 3. Network issues
    echo    - Check your internet connection
    echo    - Try again later
    echo.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo SUCCESS! Repository uploaded to GitHub!
echo ======================================================================
echo.
echo Your repository is now available at:
echo %GITHUB_URL%
echo.
echo Next steps:
echo 1. Visit your repository on GitHub
echo 2. Add description and topics
echo 3. Enable Issues and Discussions
echo 4. Add screenshots (optional)
echo 5. Create a release (optional)
echo.
echo See GITHUB_SETUP.md for more details.
echo.
pause
