
import asyncio
import websockets

async def receive_data():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri) as websocket:
            print("[CLIENT] Connected to server.")
            while True:
                message = await websocket.recv()
                print(f"[CLIENT RECEIVED] {message}")
    except Exception as e:
        print(f"[CLIENT ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(receive_data())
