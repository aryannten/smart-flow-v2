# SMART FLOW v2 - Troubleshooting Guide

## 🚫 Problem: Not Detecting Vehicles

### Possible Causes & Solutions:

#### 1. **Confidence Threshold Too High**
**Symptom**: Few or no detections, even when vehicles are visible

**Solution**: Lower the confidence threshold
```bash
# Try lower confidence
python main.py --source "YOUR_URL" --live --confidence 0.3

# Or even lower for difficult conditions
python main.py --source "YOUR_URL" --live --confidence 0.2
```

#### 2. **Night Enhancement Interfering** (NEW FIX)
**Symptom**: Worked before, stopped after update

**Solution**: Night enhancement is now OFF by default
```bash
# Normal detection (default - should work)
python main.py --source "YOUR_URL" --live

# Only enable for actual night videos
python main.py --source "YOUR_URL" --live --enhance-night
```

#### 3. **Video Quality Issues**
**Symptom**: Blurry or low-resolution stream

**Solution**: Check stream quality
```bash
# Test with local video first
python main.py --source data/testvid.mp4

# If local works but YouTube doesn't, it's a stream quality issue
```

#### 4. **Camera Angle**
**Symptom**: Detections work sometimes but not others

**Solution**: YOLO works best with:
- Side view of vehicles (not directly front/back)
- Clear vehicle profiles
- Vehicles not too small in frame

#### 5. **Frame Skipping Too Aggressive**
**Symptom**: Intermittent detections

**Solution**: Reduce or disable frame skipping
```bash
# No frame skipping
python main.py --source "YOUR_URL" --live --skip-frames 0
```

## 🎯 Quick Fixes

### Fix 1: Use Default Settings
```bash
run_youtube_fixed.bat
```
This uses proven settings that should work.

### Fix 2: Test with Local Video First
```bash
python main.py --source data/testvid.mp4
```
If this works, the issue is with the YouTube stream, not the detector.

### Fix 3: Lower Confidence
```bash
python main.py --source "YOUR_URL" --live --confidence 0.3
```

### Fix 4: Enable Tracking
```bash
python main.py --source "YOUR_URL" --live --enable-tracking --confidence 0.4
```
Tracking helps maintain detections across frames.

## 🌙 Night Detection Issues

### For Dark/Night Videos:
```bash
run_youtube_night.bat
```

Or manually:
```bash
python main.py --source "YOUR_URL" --live --enhance-night --confidence 0.4 --enable-tracking
```

### For Daytime Videos:
```bash
# DO NOT use --enhance-night for daytime!
python main.py --source "YOUR_URL" --live --confidence 0.5
```

## 🐌 Performance Issues

### If Too Slow:
```bash
run_youtube_fast.bat
```

Or manually:
```bash
python main.py --source "YOUR_URL" --live --skip-frames 1 --confidence 0.6
```

### If Still Too Slow:
```bash
run_youtube_ultra_fast.bat
```

## 🔍 Diagnostic Steps

### Step 1: Test Local Video
```bash
python main.py --source data/testvid.mp4
```
**Expected**: Should detect 8-15 vehicles per frame
**If fails**: YOLO model issue, reinstall dependencies

### Step 2: Test YouTube with Default Settings
```bash
python main.py --source "YOUR_URL" --live
```
**Expected**: Should detect some vehicles
**If fails**: Try Step 3

### Step 3: Lower Confidence
```bash
python main.py --source "YOUR_URL" --live --confidence 0.3
```
**Expected**: More detections
**If fails**: Stream quality or camera angle issue

### Step 4: Check Console Output
Look for:
```
Frame 30: Vehicles: 0, Pedestrians: 0, Emergency: 0
```
- **All zeros**: Detection not working
- **Some numbers**: Detection working but maybe low confidence

## 📊 Understanding Detection Output

### Good Detection:
```
Frame 30: Vehicles: 12, Pedestrians: 0, Emergency: 0
Frame 60: Vehicles: 15, Pedestrians: 0, Emergency: 0
Frame 90: Vehicles: 9, Pedestrians: 0, Emergency: 0
```

### Poor Detection:
```
Frame 30: Vehicles: 0, Pedestrians: 0, Emergency: 0
Frame 60: Vehicles: 1, Pedestrians: 0, Emergency: 0
Frame 90: Vehicles: 0, Pedestrians: 0, Emergency: 0
```

### Intermittent Detection (Frame Skipping):
```
Frame 30: Vehicles: 12, Pedestrians: 0, Emergency: 0
Frame 60: Vehicles: 0, Pedestrians: 0, Emergency: 0  # Skipped
Frame 90: Vehicles: 11, Pedestrians: 0, Emergency: 0
```

## 🛠️ Advanced Troubleshooting

### Check YOLO Model
```bash
# Verify model file exists
dir yolov8n.pt

# If missing, download it
# (YOLO will auto-download on first run)
```

### Check Dependencies
```bash
pip install --upgrade ultralytics opencv-python numpy
```

### Test Different Streams
Try different YouTube traffic cameras to rule out stream-specific issues.

## 💡 Best Practices

### For Live Streams:
1. Start with `run_youtube_fixed.bat`
2. If too slow, use `run_youtube_fast.bat`
3. If night video, use `run_youtube_night.bat`
4. Adjust confidence based on results

### Confidence Guidelines:
- **0.7-0.9**: Very strict, few false positives, may miss vehicles
- **0.5-0.6**: Balanced (recommended for daytime)
- **0.3-0.4**: Sensitive (recommended for night/difficult conditions)
- **0.1-0.2**: Very sensitive, more false positives

### When to Use Night Enhancement:
- ✅ Dark/night videos
- ✅ Videos with lots of headlights
- ✅ Low-light conditions
- ❌ Normal daytime videos (will reduce accuracy!)

## 📞 Still Not Working?

### Checklist:
- [ ] Tested with local video (`data/testvid.mp4`)
- [ ] Tried confidence 0.3
- [ ] Disabled night enhancement for daytime
- [ ] Checked console output for vehicle counts
- [ ] Tried different YouTube stream
- [ ] Verified YOLO model exists (`yolov8n.pt`)

### If All Else Fails:
1. Delete `yolov8n.pt` and let it re-download
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Try a different video source
4. Check if your internet connection is stable

## 🎬 Recommended Commands

### Most Reliable (Start Here):
```bash
python main.py --source "YOUR_URL" --live --confidence 0.5
```

### For Night Videos:
```bash
python main.py --source "YOUR_URL" --live --enhance-night --confidence 0.4 --enable-tracking
```

### For Fast Performance:
```bash
python main.py --source "YOUR_URL" --live --skip-frames 1 --confidence 0.6
```

### For Maximum Detections:
```bash
python main.py --source "YOUR_URL" --live --confidence 0.3 --enable-tracking
```

---

**Remember**: Detection quality depends heavily on:
- Stream quality
- Camera angle
- Lighting conditions
- Vehicle size in frame
- Confidence threshold

Start with the recommended settings and adjust based on your specific stream!
