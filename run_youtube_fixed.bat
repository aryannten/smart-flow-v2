@echo off
echo ======================================================================
echo SMART FLOW v2 - YouTube Live Stream (FIXED)
echo ======================================================================
echo.
echo Settings:
echo - Normal detection (no preprocessing)
echo - Confidence: 0.5 (default)
echo - Display: 1280x720
echo - All features disabled for maximum compatibility
echo.
echo Press ESC to stop.
echo.

python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --confidence 0.5 --display-width 1280 --display-height 720

echo.
echo Done!
pause
