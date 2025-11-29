@echo off
echo ======================================================================
echo SMART FLOW v2 - YouTube Live Stream (FAST MODE)
echo ======================================================================
echo.
echo Optimizations enabled:
echo - Process every 2nd frame (skip-frames 1)
echo - Higher confidence threshold (0.6)
echo - Faster cycle interval (15 frames)
echo - Smaller display (960x540)
echo - Night detection enhancement enabled
echo.
echo Press ESC to stop.
echo.

python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --confidence 0.6 --cycle-interval 15 --skip-frames 1 --display-width 960 --display-height 540

echo.
echo Done!
pause
