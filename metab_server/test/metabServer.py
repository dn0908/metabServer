import cv2
import numpy as np
from PIL import ImageGrab
import pytesseract
import asyncio
import websockets
import json

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

rois = []
drawing = False
ix, iy = -1, -1

connected_clients = set()

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

async def handler(websocket):
    print("[SERVER] Client connected")
    connected_clients.add(websocket)
    try:
        async for _ in websocket:
            pass
    except:
        pass
    finally:
        connected_clients.remove(websocket)
        print("[SERVER] Client disconnected")


async def ocr_and_broadcast():
    await asyncio.sleep(1)
    prev_t = None
    while True:
        t_img = np.array(ImageGrab.grab(bbox=rois[0]))
        vo2_img = np.array(ImageGrab.grab(bbox=rois[1]))
        vco2_img = np.array(ImageGrab.grab(bbox=rois[2]))

        t_val = pytesseract.image_to_string(cv2.cvtColor(t_img, cv2.COLOR_RGB2BGR), config='--psm 6').strip()
        vo2_val = pytesseract.image_to_string(cv2.cvtColor(vo2_img, cv2.COLOR_RGB2BGR), config='--psm 6').strip()
        vco2_val = pytesseract.image_to_string(cv2.cvtColor(vco2_img, cv2.COLOR_RGB2BGR), config='--psm 6').strip()

        t_val = t_val.replace(' ', '').replace('I', '1').replace('|', '').replace('©', '')
        vo2_val = vo2_val.replace(' ', '').replace(',', '.')
        vco2_val = vco2_val.replace(' ', '').replace(',', '.')

        cv2.imshow("t", cv2.cvtColor(t_img, cv2.COLOR_RGB2BGR))
        cv2.imshow("vo2", cv2.cvtColor(vo2_img, cv2.COLOR_RGB2BGR))
        cv2.imshow("vco2", cv2.cvtColor(vco2_img, cv2.COLOR_RGB2BGR))

        if len(t_val) >= 4 and t_val != prev_t:
            message = json.dumps({
                "t": t_val,
                "VO2": vo2_val,
                "VCO2": vco2_val
            })
            print("[Sending]", message)
            await asyncio.gather(*[ws.send(message) for ws in connected_clients])
            prev_t = t_val

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

        await asyncio.sleep(0.1)


async def main():
    # ROI selection
    global img
    img = cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_RGB2BGR)
    cv2.namedWindow("DRAG")
    cv2.setMouseCallback("DRAG", draw_roi)
    cv2.imshow("DRAG", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if len(rois) != 3:
        print("33333333333333333")
        return

    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("[SERVER] WebSocket server running at ws://0.0.0.0:8765")
        await ocr_and_broadcast() #runinlooooop

if __name__ == "__main__":
    asyncio.run(main())
