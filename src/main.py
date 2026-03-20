import cv2
import numpy as np
# import pytesseract
import re
import csv
import os
import time
from collections import Counter
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuration
MIN_AREA = 300  # Reduced minimum area for better detection
AR_MIN, AR_MAX = 1.5, 10.0  # Wider aspect ratio range
W_OUT, H_OUT = 450, 140
PLATE_RE = re.compile(r'[A-Z]{3}[0-9]{3}[A-Z]')
BUFFER_SIZE = 1  # Reduced for immediate testing
COOLDOWN = 2  # seconds

# Debug mode - set to True to see detection details
DEBUG_MODE = True

# Test mode - set to True to bypass strict validation
TEST_MODE = True

# CSV logging setup
csv_file = os.path.abspath("C:/Users/PC/OneDrive/Documents/year3/robotics/car-number-plate-extraction/data/plates_log.csv")
data_dir = os.path.dirname(csv_file)
os.makedirs(data_dir, exist_ok=True)

if DEBUG_MODE:
    print(f"CSV file path: {csv_file}")
    print(f"Data directory: {data_dir}")
    print(f"Directory exists: {os.path.exists(data_dir)}")
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Plate Number", "Timestamp"])

def find_plate_candidates(frame):
    """Detect potential license plates in the frame"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)  # Reduced thresholds for better edge detection

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []
    if DEBUG_MODE:
        print(f"Found {len(contours)} contours")
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue

        rect = cv2.minAreaRect(cnt)
        (_, _), (w, h), _ = rect
        if w <= 0 or h <= 0:
            continue

        ar = max(w, h) / max(1.0, min(w, h))
        if DEBUG_MODE and i < 5:  # Debug first 5 candidates
            print(f"Contour {i}: area={area:.0f}, ar={ar:.2f}")
        
        if AR_MIN <= ar <= AR_MAX:
            candidates.append(rect)
            if DEBUG_MODE:
                print(f"  -> Accepted candidate!")

    return candidates

def order_points(pts):
    """Order corner points for perspective transform"""
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)

def warp_plate(frame, rect):
    """Apply perspective correction to align the plate"""
    box = cv2.boxPoints(rect)
    src = order_points(box)

    dst = np.array([
        [0, 0],
        [W_OUT - 1, 0],
        [W_OUT - 1, H_OUT - 1],
        [0, H_OUT - 1]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(frame, M, (W_OUT, H_OUT))
    return warped

def read_plate_text(plate_img):
    """Extract text from plate image using Tesseract OCR"""
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        thresh,
        config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )

    return text.strip().replace(" ", "").replace("-", ""), thresh

def extract_valid_plate(text):
    """Validate plate format using regex"""
    text = text.upper().replace(" ", "")
    m = PLATE_RE.search(text)
    if m:
        return m.group(0)
    return None

def majority_vote(buffer):
    """Determine most common plate in buffer"""
    if not buffer:
        return None
    return Counter(buffer).most_common(1)[0][0]

def save_plate_to_csv(plate_number):
    """Save confirmed plate to CSV file"""
    try:
        if DEBUG_MODE:
            print(f"Attempting to save to: {csv_file}")
        
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                plate_number,
                time.strftime("%Y-%m-%d %H:%M:%S")
            ])
        
        if DEBUG_MODE:
            print(f"Successfully saved! File size: {os.path.getsize(csv_file)} bytes")
            
    except Exception as e:
        print(f"ERROR saving to CSV: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"CSV file path: {csv_file}")

def main():
    """Main pipeline integrating all components"""
    print("Starting Number Plate Recognition Pipeline...")
    print("Press 'q' to quit")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Camera not opened")

    plate_buffer = []
    last_saved_plate = None
    last_saved_time = 0
    frame_count = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame_count += 1
        vis = frame.copy()
        
        # Stage 1: Plate Detection
        candidates = find_plate_candidates(frame)
        
        msg = "1. Detecting plates..."
        color = (0, 200, 255)
        plate_img = None
        thresh = None
        confirmed_plate = None

        if candidates:
            msg = "2. Plate detected - Processing..."
            color = (0, 255, 0)
            
            # Choose largest candidate
            rect = max(candidates, key=lambda r: r[1][0] * r[1][1])
            box = cv2.boxPoints(rect).astype(int)

            # Draw detection box
            cv2.polylines(vis, [box], True, (255, 0, 0), 2)

            # Stage 2: Plate Alignment
            plate_img = warp_plate(frame, rect)
            
            # Stage 3: OCR Extraction
            raw_text, thresh = read_plate_text(plate_img)
            
            if DEBUG_MODE:
                print(f"OCR Result: '{raw_text}'")
            
            # Stage 4: Plate Validation
            valid_plate = extract_valid_plate(raw_text)
            
            # In test mode, accept any text with 1+ chars (for testing)
            if TEST_MODE and len(raw_text) >= 1 and not valid_plate:
                valid_plate = raw_text[:7].upper()  # Take first 7 chars as "plate"
                if DEBUG_MODE:
                    print(f"TEST MODE: Using '{valid_plate}' as plate (length={len(raw_text)})")
            
            if valid_plate:
                msg = "3. Valid plate format"
                
                # Stage 5: Temporal Confirmation
                plate_buffer.append(valid_plate)
                if len(plate_buffer) > BUFFER_SIZE:
                    plate_buffer.pop(0)

                confirmed_plate = majority_vote(plate_buffer)
                
                if confirmed_plate:
                    msg = f"4. CONFIRMED: {confirmed_plate}"
                    
                    # Stage 6: Save confirmed plate
                    now = time.time()
                    if (confirmed_plate != last_saved_plate and 
                        (now - last_saved_time) > COOLDOWN):
                        save_plate_to_csv(confirmed_plate)
                        print(f"[SAVED] {confirmed_plate} at {time.strftime('%H:%M:%S')}")
                        last_saved_plate = confirmed_plate
                        last_saved_time = now
                        msg = f"5. SAVED: {confirmed_plate}"

            # Display OCR results
            x = int(np.max(box[:, 0])) - 300
            y = int(np.max(box[:, 1])) + 25
            x = min(max(x, 10), vis.shape[1] - 350)
            y = min(max(y, 30), vis.shape[0] - 10)

            if confirmed_plate:
                cv2.putText(vis, f"FINAL: {confirmed_plate}", (x, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            elif valid_plate:
                cv2.putText(vis, f"VALID: {valid_plate}", (x, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
            elif raw_text:
                cv2.putText(vis, f"OCR: {raw_text}", (x, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

        # Display status
        cv2.putText(vis, msg, (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(vis, f"Frame: {frame_count}", (20, 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(vis, "Press q to quit", (20, vis.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Show all pipeline stages
        cv2.imshow("Number Plate Recognition Pipeline", vis)
        
        if plate_img is not None:
            cv2.imshow("Aligned Plate", plate_img)
        if thresh is not None:
            cv2.imshow("OCR Processing", thresh)

        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Pipeline stopped.")

if __name__ == "__main__":
    main()