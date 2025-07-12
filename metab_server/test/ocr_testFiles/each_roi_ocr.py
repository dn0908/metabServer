import cv2
import pytesseract
import numpy as np
from PIL import ImageGrab

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

rois = []
drawing = False
ix, iy = -1, -1

def draw_roi(event, x, y, flags, param):
    global drawing, ix, iy, rois

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        img_copy = img.copy()
        cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow("DRAG", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x1, y1 = min(ix, x), min(iy, y)
        x2, y2 = max(ix, x), max(iy, y)
        rois.append((x1, y1, x2, y2))
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        cv2.imshow("DRAG", img)

img = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
cv2.namedWindow("DRAG")
cv2.setMouseCallback("DRAG", draw_roi)
cv2.imshow("DRAG", img)
print("0_0")
cv2.waitKey(0)
cv2.destroyAllWindows()

if len(rois) != 3:
    print("333333333")
    exit()

def extract_last_number(bbox):
    region = np.array(ImageGrab.grab(bbox=bbox))
    region = cv2.cvtColor(region, cv2.COLOR_RGB2BGR)
    text = pytesseract.image_to_string(region, config='--psm 6')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    return lines[-1]

prev_t = None

try:
    while True:
        t_img = np.array(ImageGrab.grab(bbox=rois[0]))
        vo2_img = np.array(ImageGrab.grab(bbox=rois[1]))
        vco2_img = np.array(ImageGrab.grab(bbox=rois[2]))

        # for windows
        t_img_bgr = cv2.cvtColor(t_img, cv2.COLOR_RGB2BGR)
        vo2_img_bgr = cv2.cvtColor(vo2_img, cv2.COLOR_RGB2BGR)
        vco2_img_bgr = cv2.cvtColor(vco2_img, cv2.COLOR_RGB2BGR)

        t_val = pytesseract.image_to_string(t_img_bgr, config='--psm 6').strip()
        vo2_val = pytesseract.image_to_string(vo2_img_bgr, config='--psm 6').strip()
        vco2_val = pytesseract.image_to_string(vco2_img_bgr, config='--psm 6').strip()

        # show windows
        cv2.imshow("Time (t)", t_img_bgr)
        cv2.imshow("VO2", vo2_img_bgr)
        cv2.imshow("VCO2", vco2_img_bgr)

        t_val = t_val.replace(' ', '').replace('I', '1').replace('|', '').replace('©', '')
        vo2_val = vo2_val.replace(' ', '').replace(',', '.')
        vco2_val = vco2_val.replace(' ', '').replace(',', '.')

        if len(t_val) >= 4 and t_val != prev_t:
            print(f"[data] t: {t_val}, VO2: {vo2_val}, VCO2: {vco2_val}")
            prev_t = t_val

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nuser interrupt")

cv2.destroyAllWindows()
