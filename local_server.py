
import asyncio
from websockets.asyncio.server import serve

connected_clients = set()

async def handler(websocket):
    print("[SERVER] Client connected.")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"[RECEIVED] {message}")
    except Exception as e:
        print(f"[ERROR] Client disconnected with error: {e}")
    finally:
        connected_clients.remove(websocket)
        print("[SERVER] Client disconnected.")

async def main():
    async with serve(handler, "localhost", 8765):
        print("[SERVER] WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
