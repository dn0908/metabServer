import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

drawing = False
ix, iy = -1, -1
rx, ry, rw, rh = 0, 0, 0, 0
roi_selected = False

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rx, ry, rw, rh, roi_selected

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        img_temp = img.copy()
        cv2.rectangle(img_temp, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow("SELECT ROI", img_temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rx, ry, rw, rh = min(ix, x), min(iy, y), abs(ix - x), abs(iy - y)
        roi_selected = True
        cv2.rectangle(img, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
        cv2.imshow("SELECT ROI", img)

img = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
cv2.namedWindow("SELECT ROI")
cv2.setMouseCallback("SELECT ROI", draw_rectangle)
cv2.imshow("SELECT ROI", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

import re


def parse_data_line(line):
    match = re.search(r'(\d{1,2}:\d{2})\s+(\d+)[\s\t]+(\d+)', line)
    if match:
        t, vo2, vco2 = match.groups()
        return {'t': t, 'VO2': int(vo2), 'VCO2': int(vco2)}
    return None

def get_last_data_row(roi_img):
    text = pytesseract.image_to_string(roi_img)
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    if len(lines) <= 2:
        return None  # no data yet

    data_lines = lines[2:]  # skip header and unit
    for row in reversed(data_lines):
        parsed = parse_data_line(row)
        if parsed:
            return parsed  # parse only last row
    return None

if roi_selected:
    prev_row = ""
    prev_time = None

    try:
        while True:
            frame = np.array(ImageGrab.grab(bbox=(rx, ry, rx + rw, ry + rh)))
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            last_data = get_last_data_row(frame)
            if last_data:
                current_time = last_data['t']
                if current_time != prev_time:
                    print(f"[DATA DETECTED] t: {last_data['t']}, VO2: {last_data['VO2']}, VCO2: {last_data['VCO2']}")
                    prev_time = current_time

            # if last_data and last_data != prev_row:
            #     print(f"[UPDATED] t: {last_data['t']}, VO2: {last_data['VO2']}, VCO2: {last_data['VCO2']}")
            #     prev_row = last_data

            # 
            preview = frame.copy()
            cv2.putText(preview, "ctrC EXIT", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            cv2.imshow("ROI", preview)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\nstopped user intrpt")
    finally:
        cv2.destroyAllWindows()
else:
    print("roi not selected errrrrr")
