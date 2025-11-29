@echo off
echo ======================================================================
echo SMART FLOW v2 - Simulation with Web Dashboard
echo ======================================================================
echo.
echo Starting simulation with web dashboard...
echo Dashboard will be available at: http://localhost:8080
echo.
echo Press ESC in the video window to stop.
echo.

python main.py --source data/testvid.mp4 --output logs/dashboard_simulation.json --enable-pedestrians --enable-emergency --enable-tracking --enable-heatmap --dashboard --dashboard-port 8080

echo.
echo Simulation complete!
echo.
pause
