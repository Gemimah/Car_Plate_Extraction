# Number Plate Recognition Pipeline

A complete computer vision pipeline for automatic license plate detection and recognition using OpenCV and Tesseract OCR.

## 🎯 Overview

This project implements a full number plate recognition system that:
1. **Captures frames** from a webcam
2. **Detects license plates** using edge detection and contour analysis
3. **Aligns plates** with perspective correction
4. **Extracts text** using Tesseract OCR
5. **Validates plate format** with regex patterns
6. **Confirms plates** through temporal verification
7. **Saves results** to CSV file with timestamps

## 🚀 Features

- **Real-time Processing**: Live camera feed with immediate plate detection
- **Robust Detection**: Adaptive edge detection with configurable parameters
- **Perspective Correction**: 4-point transform for plate alignment
- **OCR Integration**: Tesseract OCR with optimized preprocessing
- **Format Validation**: Regex-based plate format checking
- **Temporal Confirmation**: Majority voting across multiple frames
- **Data Logging**: Automatic CSV export with timestamps
- **Debug Mode**: Comprehensive logging for troubleshooting
- **Test Mode**: Bypass strict validation for development/testing

## 📋 Requirements

### System Dependencies
- Python 3.8+
- Tesseract OCR Engine

### Python Packages
```bash
pip install -r requirements.txt
```

### Tesseract Installation
1. Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install with default settings
3. Add to PATH or specify path in code

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd car-number-plate-extraction
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Tesseract OCR**
- Windows: Download installer from official repo
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

5. **Configure Tesseract path** (if needed)
Edit `src/main.py` and update:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 🎮 Usage

### Basic Usage
```bash
cd src
python main.py
```

### Controls
- **'q'**: Quit the application
- **ESC**: Alternative quit key

### Windows Display
- **Main Window**: Live camera feed with detection boxes and OCR results
- **Aligned Plate**: Perspective-corrected plate image
- **OCR Processing**: Binary image sent to Tesseract

## ⚙️ Configuration

### Detection Parameters
```python
MIN_AREA = 300          # Minimum contour area (pixels)
AR_MIN, AR_MAX = 1.5, 10.0  # Aspect ratio range
W_OUT, H_OUT = 450, 140     # Output plate dimensions
```

### Temporal Parameters
```python
BUFFER_SIZE = 1          # Frames needed for confirmation
COOLDOWN = 2             # Seconds between saves
```

### Validation
```python
PLATE_RE = re.compile(r'[A-Z]{3}[0-9]{3}[A-Z]')  # Default format
```

### Debug Options
```python
DEBUG_MODE = True        # Show detailed logging
TEST_MODE = True         # Bypass strict validation
```

## 📊 Pipeline Stages

### Stage 1: Plate Detection
- Grayscale conversion
- Gaussian blur (5x5 kernel)
- Canny edge detection
- Contour analysis with area/aspect ratio filtering

### Stage 2: Plate Alignment
- Minimum area rectangle detection
- Corner point ordering
- Perspective transformation
- 450x140 pixel output

### Stage 3: OCR Extraction
- Grayscale conversion
- Gaussian blur
- Otsu thresholding
- Tesseract OCR with character whitelist

### Stage 4: Plate Validation
- Uppercase conversion
- Regex pattern matching
- Format validation

### Stage 5: Temporal Confirmation
- Buffer accumulation
- Majority voting
- Duplicate prevention

### Stage 6: Data Logging
- CSV file creation
- Timestamped entries
- Error handling

## 📁 Project Structure

```
car-number-plate-extraction/
├── src/
│   ├── main.py          # Main pipeline integration
│   ├── detect.py        # Plate detection module
│   ├── align.py         # Plate alignment module
│   ├── ocr.py          # OCR processing module
│   ├── validate.py     # Validation module
│   ├── temporal.py     # Temporal confirmation module
│   └── camera.py       # Camera testing module
├── data/
│   └── plates_log.csv   # Output data file
├── screenshots/         # Documentation images
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📈 Output Format

### CSV Structure
```csv
Plate Number,Timestamp
ABC123D,2026-03-19 12:30:45
XYZ789A,2026-03-19 12:31:02
```

### Console Output
```
Starting Number Plate Recognition Pipeline...
CSV file path: C:/path/to/data/plates_log.csv
Found 12 contours
  -> Accepted candidate!
OCR Result: 'ABC123D'
TEST MODE: Using 'ABC123D' as plate (length=7)
4. CONFIRMED: ABC123D
[SAVED] ABC123D at 12:30:45
5. SAVED: ABC123D
```

## 🐛 Troubleshooting

### Common Issues

**TesseractNotFoundError**
```bash
# Solution: Install Tesseract OCR
# Windows: Download from official repo
# Linux: sudo apt-get install tesseract-ocr
# Mac: brew install tesseract
```

**No plates detected**
- Increase lighting on license plate
- Hold plate steady and closer to camera
- Reduce MIN_AREA parameter
- Adjust AR_MIN/AR_MAX values

**Poor OCR results**
- Ensure good lighting conditions
- Clean plate surface
- Adjust camera focus
- Modify Tesseract configuration

**File not saving**
- Check directory permissions
- Verify CSV file path
- Check debug output for errors

### Debug Mode
Enable `DEBUG_MODE = True` to see:
- Contour detection details
- OCR processing results
- File saving operations
- Error messages

### Test Mode
Enable `TEST_MODE = True` to:
- Bypass strict validation
- Accept shorter text strings
- Test pipeline functionality

## 🔧 Advanced Configuration

### Custom Plate Formats
```python
# Modify PLATE_RE for different formats
PLATE_RE = re.compile(r'[A-Z]{2}[0-9]{4}')  # AB1234 format
PLATE_RE = re.compile(r'[0-9]{3}-[A-Z]{3}')  # 123-ABC format
```

### Camera Settings
```python
# Modify camera initialization
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)
```

### OCR Optimization
```python
# Modify Tesseract configuration
config = '--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
```

## 📝 Development Notes

### Module Structure
- Each pipeline stage is modularized
- Functions can be used independently
- Easy to extend and modify

### Performance Considerations
- Real-time processing ~30 FPS
- Memory efficient with buffer management
- Optimized for standard license plates

### Future Enhancements
- Multiple camera support
- Machine learning plate detection
- Database integration
- Web interface
- Mobile deployment

## 📄 License

This project is for educational purposes. Please ensure compliance with local regulations regarding license plate recognition systems.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Enable debug mode for detailed logs
3. Review console output
4. Verify Tesseract installation

---

**Note**: This system is designed for educational and development purposes. Ensure compliance with local privacy laws and regulations when deploying in production environments.