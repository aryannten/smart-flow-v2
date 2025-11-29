@echo off
echo ======================================================================
echo SMART FLOW v2 - YouTube Live Stream (NIGHT MODE)
echo ======================================================================
echo.
echo Settings for night/dark videos:
echo - Night enhancement: ON
echo - Lower confidence: 0.4 (more sensitive)
echo - Tracking enabled
echo - Display: 1280x720
echo.
echo Use this for streams with headlights or low light!
echo.
echo Press ESC to stop.
echo.

python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --enhance-night --confidence 0.4 --enable-tracking --display-width 1280 --display-height 720

echo.
echo Done!
pause
