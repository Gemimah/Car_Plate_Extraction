# Number Plate Recognition Pipeline

A complete computer vision pipeline for automatic license plate detection and recognition using OpenCV and Tesseract OCR.

## 🎯 Overview

This project is a real-time computer vision pipeline that detects and recognizes vehicle license plates using OpenCV and Tesseract OCR. It captures frames from a webcam, identifies plates through edge detection and contour analysis, aligns them using perspective transformation, and extracts text via OCR. The system then validates the plate format using regex, confirms results across multiple frames to improve accuracy, and saves the recognized plate numbers with timestamps in a CSV file. It includes features like debug and test modes for easier development, and its performance depends on factors such as lighting, camera quality, and proper Tesseract installation.

**Note**: This system is designed for educational and development purposes. Ensure compliance with local privacy laws and regulations when deploying in production environments.
