@echo off
echo ======================================================================
echo SMART FLOW v2 - YouTube Live Stream
echo ======================================================================
echo.
echo This will run SMART FLOW with a YouTube live stream.
echo.
set /p YOUTUBE_URL="Enter YouTube URL (or press Enter for demo): "

if "%YOUTUBE_URL%"=="" (
    echo Using demo video instead...
    python main.py --source data/testvid.mp4 --enable-tracking --enable-heatmap
) else (
    echo.
    echo Starting SMART FLOW with YouTube stream...
    echo URL: %YOUTUBE_URL%
    echo.
    echo Press ESC in the video window to stop.
    echo.
    python main.py --source "%YOUTUBE_URL%" --live --enable-tracking --enable-heatmap --output logs/youtube_simulation.json
)

echo.
echo Simulation complete!
echo.
pause
