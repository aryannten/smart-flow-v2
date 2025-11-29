# SMART FLOW v2 - Project Structure

## 📁 Directory Structure

```
smart-flow-v2/
├── 📄 README.md                    # Main project documentation
├── 📄 QUICKSTART_LOCAL.md          # Quick start guide
├── 📄 SETUP_V2.md                  # Setup instructions
├── 📄 main.py                      # Main application entry point
├── 📄 run_local.py                 # Interactive launcher
├── 📄 run_basic.bat                # Windows quick start (basic)
├── 📄 run_with_dashboard.bat       # Windows quick start (dashboard)
├── 📄 requirements.txt             # Python dependencies
├── 📄 pytest.ini                   # Test configuration
├── 📄 yolov8n.pt                   # YOLO model file
├── 📄 .gitignore                   # Git ignore rules
│
├── 📂 src/                         # Source code
│   ├── advanced_signal_controller.py
│   ├── config_loader.py
│   ├── emergency_priority_handler.py
│   ├── enhanced_detector.py
│   ├── enhanced_traffic_analyzer.py
│   ├── enhanced_visualizer.py
│   ├── error_handler.py
│   ├── metrics_logger.py
│   ├── models.py
│   ├── multi_intersection_coordinator.py
│   ├── pedestrian_manager.py
│   ├── queue_estimator.py
│   ├── signal_controller.py
│   ├── stream_manager.py
│   ├── time_weather_adapter.py
│   ├── traffic_analyzer.py
│   ├── turn_lane_controller.py
│   ├── vehicle_detector.py
│   ├── video_processor.py
│   ├── video_writer.py
│   ├── visualizer.py
│   ├── web_dashboard.py
│   └── __init__.py
│
├── 📂 tests/                       # Test suite (378 tests)
│   ├── test_advanced_signal_controller.py
│   ├── test_config_loader.py
│   ├── test_emergency_priority_handler.py
│   ├── test_enhanced_detector.py
│   ├── test_enhanced_traffic_analyzer.py
│   ├── test_enhanced_traffic_analyzer_requirements.py
│   ├── test_error_handler.py
│   ├── test_integration.py
│   ├── test_metrics_logger.py
│   ├── test_multi_intersection_coordinator.py
│   ├── test_pedestrian_manager.py
│   ├── test_properties.py
│   ├── test_queue_estimator.py
│   ├── test_signal_controller.py
│   ├── test_stream_manager.py
│   ├── test_time_weather_adapter.py
│   ├── test_traffic_analyzer.py
│   ├── test_turn_lane_controller.py
│   ├── test_vehicle_detector.py
│   ├── test_video_processor.py
│   ├── test_visualizer.py
│   ├── test_web_dashboard.py
│   └── __init__.py
│
├── 📂 config/                      # Configuration examples
│   ├── comprehensive_intersection_example.json
│   ├── comprehensive_intersection_example.yaml
│   ├── dashboard_config.json
│   ├── multi_intersection_config.json
│   ├── multi_intersection_network_example.yaml
│   ├── network_example.json
│   ├── simple_intersection_example.yaml
│   ├── single_intersection_config.json
│   └── README.md
│
├── 📂 docs/                        # Documentation
│   ├── api_documentation.md
│   ├── configuration_guide.md
│   ├── configuration_schema.md
│   ├── deployment_guide.md
│   ├── time_weather_adapter_usage.md
│   ├── websocket_protocol.md
│   └── web_dashboard_usage.md
│
├── 📂 data/                        # Data files
│   ├── testvid.mp4                 # Test video
│   ├── lane_config_example.json
│   └── README.md
│
├── 📂 examples/                    # Example scripts
│   ├── time_weather_adapter_demo.py
│   └── web_dashboard_demo.py
│
├── 📂 dashboard/                   # Web dashboard
│   ├── frontend/                   # React frontend
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── QUICKSTART.md
│   └── README.md
│
└── 📂 .kiro/                       # Kiro IDE specs
    └── specs/
        └── smart-flow-v2/
            ├── requirements.md     # Feature requirements
            ├── design.md           # Design document
            └── tasks.md            # Implementation tasks
```

## 🗂️ Key Files

### Entry Points
- **main.py** - Main application (run simulations)
- **run_local.py** - Interactive launcher with menu
- **run_basic.bat** - Windows quick start (basic mode)
- **run_with_dashboard.bat** - Windows quick start (with dashboard)

### Documentation
- **README.md** - Main project documentation
- **QUICKSTART_LOCAL.md** - Quick start guide
- **SETUP_V2.md** - Detailed setup instructions
- **docs/** - Comprehensive documentation

### Source Code
- **src/** - All Python source code
  - Core: models.py, signal_controller.py, traffic_analyzer.py
  - Enhanced: enhanced_detector.py, enhanced_visualizer.py
  - Managers: pedestrian_manager.py, emergency_priority_handler.py
  - Infrastructure: stream_manager.py, web_dashboard.py

### Tests
- **tests/** - Complete test suite (378 tests, 76% coverage)
  - Unit tests for all components
  - Integration tests
  - Property-based tests

### Configuration
- **config/** - Example configurations
  - Single intersection examples
  - Multi-intersection network examples
  - Dashboard configuration

## 🚀 Quick Access

### Run the System
```bash
# Interactive menu
python run_local.py

# Direct command
python main.py --source data/testvid.mp4

# With dashboard
python main.py --source data/testvid.mp4 --dashboard
```

### Run Tests
```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### View Documentation
- Main docs: `docs/`
- API reference: `docs/api_documentation.md`
- Configuration: `docs/configuration_guide.md`
- Dashboard: `docs/web_dashboard_usage.md`

## 📊 Generated Files (Ignored by Git)

These directories are created during runtime:
- **logs/** - Simulation metrics and error logs
- **output/** - Annotated video outputs
- **htmlcov/** - Test coverage reports
- **.pytest_cache/** - Pytest cache
- **.hypothesis/** - Hypothesis test data
- **__pycache__/** - Python bytecode cache

## 🔧 Configuration Files

- **pytest.ini** - Test configuration
- **requirements.txt** - Python dependencies
- **.gitignore** - Git ignore rules
- **config/*.json** - Intersection configurations
- **config/*.yaml** - Network configurations

## 📝 Spec Files

Located in `.kiro/specs/smart-flow-v2/`:
- **requirements.md** - Formal requirements (EARS format)
- **design.md** - System design and architecture
- **tasks.md** - Implementation task list

## 🎯 Important Notes

1. **YOLO Model**: `yolov8n.pt` must be in root directory
2. **Test Video**: `data/testvid.mp4` is included for testing
3. **Logs**: Created automatically in `logs/` directory
4. **Output**: Videos saved to `output/` directory
5. **Dashboard**: Frontend in `dashboard/frontend/`

## 🧹 Cleanup

To clean generated files:
```bash
# Remove logs and output
rm -rf logs/ output/ htmlcov/

# Remove Python cache
rm -rf __pycache__/ .pytest_cache/ .hypothesis/

# Remove coverage data
rm .coverage
```

Or use Git:
```bash
git clean -fdx
```

## 📦 Dependencies

See `requirements.txt` for full list. Key dependencies:
- opencv-python - Computer vision
- ultralytics - YOLOv8 model
- numpy - Numerical computing
- fastapi - Web framework
- pytest - Testing framework
- hypothesis - Property-based testing

## 🎓 Learning Resources

- **Specs**: `.kiro/specs/smart-flow-v2/` - Formal specifications
- **Tests**: `tests/` - Example usage and test cases
- **Examples**: `examples/` - Demo scripts
- **Docs**: `docs/` - Comprehensive guides

---

For more information, see [README.md](README.md)
