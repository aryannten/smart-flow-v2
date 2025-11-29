# SMART FLOW v2 - Performance Optimization Guide

## 🐌 Problem: Slow/Laggy Live Stream

### Causes:
1. **High Resolution** - 1920x1080 is computationally expensive
2. **YOLO Processing** - AI detection on every frame
3. **CPU-Only** - No GPU acceleration
4. **Network Latency** - YouTube stream buffering

## ⚡ Solutions

### Quick Fix: Use Optimized Batch Files

#### 1. Fast Mode (Recommended)
```bash
run_youtube_fast.bat
```
- Processes every 2nd frame
- 2x faster performance
- Still accurate detection

#### 2. Ultra Fast Mode
```bash
run_youtube_ultra_fast.bat
```
- Processes every 3rd frame
- 3x faster performance
- Good for slow computers

### Manual Optimization

#### Option 1: Skip Frames
```bash
# Process every 2nd frame (2x faster)
python main.py --source "YOUR_URL" --live --skip-frames 1

# Process every 3rd frame (3x faster)
python main.py --source "YOUR_URL" --live --skip-frames 2

# Process every 4th frame (4x faster)
python main.py --source "YOUR_URL" --live --skip-frames 3
```

#### Option 2: Increase Confidence Threshold
```bash
# Higher threshold = fewer detections = faster
python main.py --source "YOUR_URL" --live --confidence 0.7
```

#### Option 3: Reduce Display Size
```bash
# Smaller window = faster rendering
python main.py --source "YOUR_URL" --live --display-width 800 --display-height 450
```

#### Option 4: Disable Heavy Features
```bash
# No tracking, no heatmap
python main.py --source "YOUR_URL" --live
```

#### Option 5: Combine All Optimizations
```bash
python main.py --source "YOUR_URL" --live \
  --skip-frames 2 \
  --confidence 0.7 \
  --cycle-interval 10 \
  --display-width 800 \
  --display-height 450
```

## 🌙 Problem: Night Detection / Headlight Issues

### Causes:
1. **Low Light** - YOLO trained mostly on daytime images
2. **Headlight Glare** - Bright lights wash out vehicle features
3. **Contrast Issues** - Dark vehicles on dark roads

### ✅ Solution: Automatic Night Enhancement

The system now includes automatic preprocessing that:
- ✅ **Enhances contrast** in dark areas
- ✅ **Reduces headlight glare** 
- ✅ **Improves vehicle visibility** at night
- ✅ **Works automatically** - no configuration needed

This is enabled by default in all modes!

### Additional Tips for Night Detection:

1. **Increase Confidence Threshold**
   ```bash
   --confidence 0.4  # Lower threshold for night (more detections)
   ```

2. **Use Tracking**
   ```bash
   --enable-tracking  # Helps maintain detection across frames
   ```

3. **Adjust Cycle Interval**
   ```bash
   --cycle-interval 45  # Longer interval for more stable detection
   ```

## 📊 Performance Comparison

| Mode | Frame Skip | Speed | Accuracy | Best For |
|------|-----------|-------|----------|----------|
| **Normal** | 0 | 1x | 100% | Offline analysis |
| **Fast** | 1 | 2x | 95% | Live monitoring |
| **Ultra Fast** | 2 | 3x | 90% | Slow computers |
| **Maximum** | 3 | 4x | 85% | Very slow systems |

## 🎯 Recommended Settings

### For Live YouTube Streams:
```bash
python main.py --source "YOUR_URL" --live \
  --skip-frames 1 \
  --confidence 0.6 \
  --display-width 960 \
  --display-height 540
```

### For Night Streams:
```bash
python main.py --source "YOUR_URL" --live \
  --skip-frames 1 \
  --confidence 0.4 \
  --enable-tracking \
  --cycle-interval 45
```

### For Slow Computers:
```bash
python main.py --source "YOUR_URL" --live \
  --skip-frames 2 \
  --confidence 0.7 \
  --display-width 800 \
  --display-height 450 \
  --cycle-interval 10
```

### For Maximum Accuracy (Offline):
```bash
python main.py --source "video.mp4" \
  --skip-frames 0 \
  --confidence 0.5 \
  --enable-tracking \
  --enable-heatmap \
  --enable-trajectories
```

## 🔧 Advanced Optimizations

### 1. Use GPU Acceleration (If Available)
Install CUDA-enabled PyTorch:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 2. Lower YouTube Stream Quality
The system automatically selects the best quality. For slower connections, YouTube may buffer less with lower quality.

### 3. Use Local Video Files
Download the stream first for smoother playback:
```bash
yt-dlp "YOUR_URL" -o traffic.mp4
python main.py --source traffic.mp4
```

### 4. Headless Mode
Disable display for maximum performance:
```bash
python main.py --source "YOUR_URL" --live --no-display --save-video output.mp4
```

## 📈 Monitoring Performance

Watch the console output:
```
Frame 30: Vehicles: 12, Pedestrians: 0, Emergency: 0
Throttling: CPU=92.3%, Memory=65.3%
```

- **CPU > 90%**: System is maxed out, use more optimizations
- **CPU < 70%**: You can enable more features
- **Throttling messages**: Normal, system is protecting itself

## 💡 Tips

1. **Start with Fast Mode** - Use `run_youtube_fast.bat`
2. **Adjust based on CPU** - If still slow, try Ultra Fast
3. **Night streams** - Lower confidence threshold (0.4-0.5)
4. **Test different settings** - Find what works for your system
5. **Close other apps** - Free up CPU and memory

## 🎬 Example Commands

### Balanced (Good performance + accuracy):
```bash
python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --skip-frames 1 --confidence 0.6 --display-width 960 --display-height 540
```

### Fast (Priority on speed):
```bash
python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --skip-frames 2 --confidence 0.7 --display-width 800 --display-height 450
```

### Accurate (Priority on detection):
```bash
python main.py --source "https://www.youtube.com/live/qMYlpMsWsBE?si=gq-wmeprYq5U-n_K" --live --skip-frames 0 --confidence 0.5 --enable-tracking
```

---

**Remember**: Frame skipping doesn't affect signal control logic - it only reduces detection frequency. The system still manages traffic signals effectively!
