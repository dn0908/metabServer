import cv2
import pyautogui
import numpy as np

drawing = False
ix, iy = -1, -1
rx, ry, rw, rh = 0, 0, 0, 0
roi_selected = False

def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rx, ry, rw, rh, roi_selected

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_temp = img.copy()
            cv2.rectangle(img_temp, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("DRAG", img_temp)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rx, ry, rw, rh = min(ix, x), min(iy, y), abs(ix - x), abs(iy - y)
        roi_selected = True
        cv2.rectangle(img, (rx, ry), (rx + rw, ry + rh), (0, 255, 0), 2)
        cv2.imshow("DRAG", img)

screenshot = pyautogui.screenshot()
img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
cv2.namedWindow("DRAG")
cv2.setMouseCallback("DRAG", draw_rectangle)
cv2.imshow("DRAG", img)
cv2.waitKey(0)
cv2.destroyWindow("DRAG")

if roi_selected:
    fps = 20.0
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('roi_record.avi', fourcc, fps, (rw, rh))

    print("press Q to stop")
    while True:
        frame = pyautogui.screenshot(region=(rx, ry, rw, rh))
        frame_np = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        out.write(frame_np)
        cv2.imshow("RECORDING FRAME", frame_np)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release()
    cv2.destroyAllWindows()
    print("saved.")
else:
    print("not selected")
