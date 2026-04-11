import asyncio
import json
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from processor import SensorProcessor

app = FastAPI()

# Initialize processors for sensors
processors = {
    "sensor-T1": SensorProcessor(window_size=60),
    "sensor-V1": SensorProcessor(window_size=60)
}

print("\n=== Server Console ===")
print("[INFO] Stream processor started — ready for sensor feed")
print("[INFO] Application running on http://localhost:8000")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[INFO] Client connected — starting live processing")
    try:
        while True:
            # Receive raw sensor data from client.py
            data = await websocket.receive_json()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Process Sensor T1
            t1_val = data.get("sensor-T1", 70)
            t1_data = processors["sensor-T1"].process(t1_val)
            
            # Process Sensor V1 (optional processing but useful for dashboard)
            v1_val = data.get("sensor-V1", 0.1)
            v1_data = processors["sensor-V1"].process(v1_val)
            
            # Console Output (as per requirements)
            print(f"[{timestamp}] sensor-T1 temp={t1_val:.1f}F vibration={v1_val:.2f}g status={t1_data['status']}")
            
            if t1_data["status"] == "CRITICAL":
                print("=== Alert Triggered ===")
                print(f"[ALERT] sensor-T1 — Temperature exceeded threshold (>100F)")
                print(f"Current: {t1_val:.1f}F | 5-min avg: {t1_data['avg']:.1f}F | Deviation: {t1_data['z_score']:.1f} sigma")
                print("Action: Notification sent to ops-team@factory.com")
                print("=======================")

    except WebSocketDisconnect:
        print("[INFO] Client disconnected")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
