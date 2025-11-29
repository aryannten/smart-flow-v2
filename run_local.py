#!/usr/bin/env python3
"""
Quick launcher for SMART FLOW v2 - Local Testing

This script provides easy commands to run the system with different configurations.
"""

import subprocess
import sys
from pathlib import Path


def run_basic():
    """Run basic simulation with test video."""
    print("Running BASIC simulation...")
    print("Features: Basic vehicle detection and signal control")
    print()
    
    cmd = [
        sys.executable, "main.py",
        "--source", "data/testvid.mp4",
        "--output", "logs/basic_simulation.json"
    ]
    
    subprocess.run(cmd)


def run_full_features():
    """Run simulation with all features enabled."""
    print("Running FULL FEATURES simulation...")
    print("Features: All v2 features enabled")
    print()
    
    cmd = [
        sys.executable, "main.py",
        "--source", "data/testvid.mp4",
        "--output", "logs/full_simulation.json",
        "--enable-pedestrians",
        "--enable-emergency",
        "--enable-turn-lanes",
        "--enable-queue-estimation",
        "--enable-tracking",
        "--enable-heatmap",
        "--enable-trajectories",
        "--save-video", "output/annotated_full.mp4"
    ]
    
    subprocess.run(cmd)


def run_with_dashboard():
    """Run simulation with web dashboard."""
    print("Running simulation with WEB DASHBOARD...")
    print("Features: All features + real-time web dashboard")
    print("Dashboard will be available at: http://localhost:8080")
    print()
    
    cmd = [
        sys.executable, "main.py",
        "--source", "data/testvid.mp4",
        "--output", "logs/dashboard_simulation.json",
        "--enable-pedestrians",
        "--enable-emergency",
        "--enable-turn-lanes",
        "--enable-queue-estimation",
        "--enable-tracking",
        "--enable-heatmap",
        "--enable-trajectories",
        "--dashboard",
        "--dashboard-port", "8080"
    ]
    
    subprocess.run(cmd)


def run_headless():
    """Run simulation in headless mode (no display window)."""
    print("Running HEADLESS simulation...")
    print("Features: All features, no display window")
    print()
    
    cmd = [
        sys.executable, "main.py",
        "--source", "data/testvid.mp4",
        "--output", "logs/headless_simulation.json",
        "--enable-pedestrians",
        "--enable-emergency",
        "--enable-turn-lanes",
        "--enable-queue-estimation",
        "--enable-tracking",
        "--no-display",
        "--save-video", "output/annotated_headless.mp4"
    ]
    
    subprocess.run(cmd)


def run_webcam():
    """Run simulation with webcam input."""
    print("Running WEBCAM simulation...")
    print("Features: Live webcam feed with all features")
    print("Press ESC to stop")
    print()
    
    cmd = [
        sys.executable, "main.py",
        "--source", "webcam:0",
        "--live",
        "--output", "logs/webcam_simulation.json",
        "--enable-pedestrians",
        "--enable-emergency",
        "--enable-tracking",
        "--enable-heatmap"
    ]
    
    subprocess.run(cmd)


def show_menu():
    """Display menu and get user choice."""
    print("=" * 70)
    print("SMART FLOW v2 - Local Testing Launcher")
    print("=" * 70)
    print()
    print("Choose a configuration to run:")
    print()
    print("1. Basic Simulation")
    print("   - Simple vehicle detection and signal control")
    print("   - Uses: data/testvid.mp4")
    print()
    print("2. Full Features")
    print("   - All v2 features enabled")
    print("   - Pedestrians, emergency vehicles, turn lanes, queue estimation")
    print("   - Heatmap and trajectory visualization")
    print("   - Saves annotated video")
    print()
    print("3. With Web Dashboard")
    print("   - All features + real-time web dashboard")
    print("   - Access at http://localhost:8080")
    print("   - Remote monitoring and control")
    print()
    print("4. Headless Mode")
    print("   - All features, no display window")
    print("   - Good for server/background processing")
    print("   - Saves annotated video")
    print()
    print("5. Webcam Live")
    print("   - Live webcam feed with detection")
    print("   - Real-time processing")
    print()
    print("0. Exit")
    print()
    print("=" * 70)
    
    choice = input("Enter your choice (0-5): ").strip()
    return choice


def main():
    """Main launcher function."""
    # Create output directories
    Path("logs").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    
    while True:
        choice = show_menu()
        print()
        
        if choice == "1":
            run_basic()
        elif choice == "2":
            run_full_features()
        elif choice == "3":
            run_with_dashboard()
        elif choice == "4":
            run_headless()
        elif choice == "5":
            run_webcam()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            continue
        
        print()
        input("Press Enter to return to menu...")
        print("\n" * 2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
