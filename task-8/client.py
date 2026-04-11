import asyncio
import json
import random
import websockets

async def simulate_sensors():
    uri = "ws://localhost:8000/ws"
    print(f"[CLIENT] Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("[CLIENT] Connection established. Sending data...")
            while True:
                # Simulate sensor readings
                # T1: Temp in F (Normal ~70-75, Anomaly 100+)
                t1_raw = 70 + random.uniform(0, 5)
                if random.random() > 0.95: # 5% chance of spike
                    t1_raw += 30
                
                # V1: Vibration in g
                v1_raw = 0.1 + random.uniform(0, 0.05)
                if random.random() > 0.98: # 2% chance of spike
                    v1_raw += 0.5
                
                payload = {
                    "sensor-T1": t1_raw,
                    "sensor-V1": v1_raw
                }
                
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"[CLIENT] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_sensors())
