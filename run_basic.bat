@echo off
echo ======================================================================
echo SMART FLOW v2 - Basic Simulation
echo ======================================================================
echo.
echo Running basic simulation with test video...
echo Press ESC in the video window to stop.
echo.

python main.py --source data/testvid.mp4 --output logs/basic_simulation.json

echo.
echo Simulation complete!
echo Check logs/basic_simulation.json for results.
echo.
pause
