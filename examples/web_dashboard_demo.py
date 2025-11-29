"""
Web Dashboard Demo for SMART FLOW v2

Demonstrates the web dashboard functionality with simulated traffic data.
"""

import time
import numpy as np
import cv2
from src.web_dashboard import WebDashboard


def create_demo_frame(frame_number: int) -> np.ndarray:
    """
    Create a demo frame with some visual content.
    
    Args:
        frame_number: Frame number for animation
        
    Returns:
        Demo frame
    """
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some animated content
    x = int(320 + 200 * np.sin(frame_number * 0.1))
    y = int(240 + 100 * np.cos(frame_number * 0.1))
    
    cv2.circle(frame, (x, y), 20, (0, 255, 0), -1)
    cv2.putText(frame, f"Frame {frame_number}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return frame


def main():
    """Run web dashboard demo"""
    print("=" * 60)
    print("SMART FLOW v2 - Web Dashboard Demo")
    print("=" * 60)
    
    # Create dashboard
    dashboard = WebDashboard(port=8080)
    
    print("\nStarting web server on http://localhost:8080")
    dashboard.start()
    
    print("\nAvailable endpoints:")
    print("  - http://localhost:8080/api/status")
    print("  - http://localhost:8080/api/metrics")
    print("  - http://localhost:8080/stream")
    print("  - ws://localhost:8080/ws")
    
    print("\nSimulating traffic data...")
    print("Press Ctrl+C to stop\n")
    
    try:
        frame_number = 0
        
        while True:
            # Create demo frame
            frame = create_demo_frame(frame_number)
            dashboard.update_video_feed(frame)
            
            # Update metrics
            metrics = {
                "timestamp": time.time(),
                "frame_number": frame_number,
                "lanes": {
                    "north": {
                        "count": 5 + int(3 * np.sin(frame_number * 0.05)),
                        "density": 0.3,
                        "signal": "green" if (frame_number // 30) % 2 == 0 else "red"
                    },
                    "south": {
                        "count": 3 + int(2 * np.cos(frame_number * 0.05)),
                        "density": 0.2,
                        "signal": "red" if (frame_number // 30) % 2 == 0 else "green"
                    },
                    "east": {
                        "count": 4 + int(2 * np.sin(frame_number * 0.03)),
                        "density": 0.25,
                        "signal": "yellow"
                    },
                    "west": {
                        "count": 6 + int(3 * np.cos(frame_number * 0.03)),
                        "density": 0.35,
                        "signal": "green"
                    }
                },
                "throughput": 120 + int(20 * np.sin(frame_number * 0.02)),
                "average_wait": 15.5 + 5 * np.cos(frame_number * 0.02)
            }
            
            dashboard.update_metrics(metrics)
            
            # Send alerts occasionally
            if frame_number % 100 == 0:
                dashboard.broadcast_alert(
                    f"System update at frame {frame_number}",
                    "info"
                )
            
            if frame_number % 200 == 0:
                dashboard.broadcast_alert(
                    "High traffic detected on north lane",
                    "warning"
                )
            
            # Check for user commands
            commands = dashboard.get_user_commands()
            if commands:
                print(f"\nReceived {len(commands)} command(s):")
                for cmd in commands:
                    print(f"  - {cmd.command_type.value}: {cmd.target} = {cmd.value}")
            
            # Display status
            if frame_number % 30 == 0:
                print(f"Frame {frame_number}: "
                      f"North={metrics['lanes']['north']['count']} "
                      f"South={metrics['lanes']['south']['count']} "
                      f"Throughput={metrics['throughput']}")
            
            frame_number += 1
            time.sleep(0.033)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("\n\nStopping dashboard...")
        dashboard.stop()
        print("Dashboard stopped.")


if __name__ == "__main__":
    main()
