import rclpy
from rclpy.node import Node
import asyncio
import websockets
import json

class MetabLogger_Node(Node):
    def __init__(self):
        super().__init__('metab_logger_node')
        self.get_logger().info("metab logger start")

    async def websocket_listener(self):
        uri = "ws://192.168.0.11:8765"
        try:
            async with websockets.connect(uri) as websocket:
                self.get_logger().info(f"connected to {uri}")
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    t = data.get("t")
                    vo2 = data.get("VO2")
                    vco2 = data.get("VCO2")
                    self.get_logger().info(f"t={t}, VO2={vo2}, VCO2={vco2}")
        except Exception as e:
            self.get_logger().error(f"WebSocket error: {e}")

async def main():
    rclpy.init()
    node = MetabLogger_Node()

    task1 = asyncio.create_task(node.websocket_listener())
    task2 = asyncio.to_thread(rclpy.spin, node)

    await asyncio.gather(task1, task2)
    rclpy.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
