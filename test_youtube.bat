@echo off
echo ======================================================================
echo SMART FLOW v2 - YouTube Live Stream Test
echo ======================================================================
echo.
echo Running with proper display size (1280x720)...
echo Press ESC to stop.
echo.

python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --enable-tracking --enable-heatmap --display-width 1280 --display-height 720

echo.
echo Test complete!
pause
