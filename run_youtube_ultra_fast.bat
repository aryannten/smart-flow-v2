@echo off
echo ======================================================================
echo SMART FLOW v2 - YouTube Live Stream (ULTRA FAST MODE)
echo ======================================================================
echo.
echo Maximum optimizations:
echo - Process every 3rd frame (skip-frames 2)
echo - High confidence threshold (0.7)
echo - Fast cycle interval (10 frames)
echo - Small display (800x450)
echo - Night detection enhancement enabled
echo.
echo Best for: Slow computers, real-time monitoring
echo.
echo Press ESC to stop.
echo.

python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --confidence 0.7 --cycle-interval 10 --skip-frames 2 --display-width 800 --display-height 450

echo.
echo Done!
pause
